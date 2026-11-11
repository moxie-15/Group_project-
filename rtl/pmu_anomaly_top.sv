// ============================================================================
// File: pmu_anomaly_top.sv
// Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
// Standard: SystemVerilog IEEE 1800-2017
// Description: Top-Level Synthesizable Entity for the Smart Grid FDI Anomaly
//              Engine. Integrates:
//              - Three-Process Moore FSM Controller (pmu_fsm_ctrl)
//              - On-Chip Block RAM State Storage (pmu_state_bram)
//              - Q1.15 Preprocessor & Mean Centering Unit
//              - Q1.15 Mahalanobis Distance Engine (mahalanobis_matrix_engine)
//              - Q1.15 Two-Sided CUSUM Filter (cusum_filter_q15)
//              - Combined Decision & Real-Time Alert Flags
// ============================================================================

`timescale 1ns / 1ps

module pmu_anomaly_top
    import fdi_pkg::*;
#(
    parameter int N = N_CHANNELS // Default 4 channels
)(
    input  logic              clk,
    input  logic              rst_n,

    // ------------------------------------------------------------------------
    // Ingestion Stream Interface (Custom Valid/Ready Handshake)
    // ------------------------------------------------------------------------
    input  logic              data_valid,
    output logic              data_ready,
    input  pmu_vec_t          pmu_sample_i,   // 4-element raw measurement vector (Q1.15)
    input  logic [CHANNEL_BITS-1:0] channel_id_i, // Target channel (0..3)

    // ------------------------------------------------------------------------
    // Configurable Reference Parameters (with calibrated grid defaults)
    // ------------------------------------------------------------------------
    input  pmu_vec_t          mu_vec_i,       // Baseline mean vector (Q1.15)
    input  pmu_vec_t          sigma_inv_i,    // 1/sigma normalization factors (Q1.15)
    input  pmu_mat_t          w_matrix_i,     // Precision matrix W = Sigma^-1 (Q1.15)
    input  q15_t              thresh_t2_i,    // Spatial threshold T^2 (Q1.15)
    input  q15_t              cusum_k_i,      // CUSUM slack allowance k (Q1.15)
    input  q15_t              cusum_h_i,      // CUSUM decision threshold h (Q1.15)
    input  q15_t              cusum_nu0_i,    // CUSUM nominal baseline nu0 (Q1.15)

    // ------------------------------------------------------------------------
    // Real-Time Anomaly Outputs & Telemetry
    // ------------------------------------------------------------------------
    output logic              fdi_alert_o,        // Master FDI alert (Spatial | Temporal)
    output logic              spatial_alert_o,    // Mahalanobis distance breach (D^2 > T^2)
    output logic              cusum_pos_alert_o,  // Positive CUSUM drift (S^+ > h)
    output logic              cusum_neg_alert_o,  // Negative CUSUM drift (S^- > h)
    output q15_t              dm2_metric_o,       // Computed D^2 (Q1.15)
    output q15_t              cusum_s_pos_o,      // Active channel S^+ state (Q1.15)
    output q15_t              cusum_s_neg_o,      // Active channel S^- state (Q1.15)
    output logic              frame_done_o,       // Frame evaluation complete
    output logic [CHANNEL_BITS-1:0] channel_active_o // Active channel pointer
);

    // ------------------------------------------------------------------------
    // Internal Control Signals from Moore FSM
    // ------------------------------------------------------------------------
    logic latch_sample_w;
    logic preprocess_en_w;
    logic mahal_start_w;
    logic cusum_en_w;
    logic decision_en_w;
    logic bram_we_w;
    logic chan_advance_w;
    logic mahal_done_w;
    fsm_state_t fsm_state_w;

    // Active Channel Pointer Register
    logic [CHANNEL_BITS-1:0] chan_ptr_q;
    logic chan_last_w;

    assign chan_last_w = (chan_ptr_q == logic [CHANNEL_BITS-1:0]'(N - 1));

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            chan_ptr_q <= '0;
        end else if (chan_advance_w) begin
            if (chan_last_w) begin
                chan_ptr_q <= '0;
            end else begin
                chan_ptr_q <= chan_ptr_q + 1'b1;
            end
        end
    end

    // ------------------------------------------------------------------------
    // Step 1: Input Latching and Preprocessing (Mean Centering & Normalization)
    // r[i] = (x[i] - mu[i]) * sigma_inv[i]
    // ------------------------------------------------------------------------
    pmu_vec_t raw_sample_q;
    pmu_vec_t residual_vec_q;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            raw_sample_q   <= '0;
            residual_vec_q <= '0;
        end else begin
            if (latch_sample_w) begin
                raw_sample_q <= pmu_sample_i;
            end
            if (preprocess_en_w) begin
                for (int i = 0; i < N; i++) begin
                    q15_t diff;
                    diff = q15_sub_sat(raw_sample_q[i], mu_vec_i[i]);
                    // Multiply centered difference by inverse standard deviation
                    residual_vec_q[i] <= q15_mult(diff, sigma_inv_i[i]);
                end
            end
        end
    end

    // ------------------------------------------------------------------------
    // Step 2: Three-Process Moore FSM Controller Instance
    // ------------------------------------------------------------------------
    pmu_fsm_ctrl u_fsm_ctrl (
        .clk            (clk),
        .rst_n          (rst_n),
        .data_valid     (data_valid),
        .data_ready     (data_ready),
        .mahal_done     (mahal_done_w),
        .channel_last   (chan_last_w),
        .latch_sample_o (latch_sample_w),
        .preprocess_en_o(preprocess_en_w),
        .mahal_start_o  (mahal_start_w),
        .cusum_en_o     (cusum_en_w),
        .decision_en_o  (decision_en_w),
        .bram_we_o      (bram_we_w),
        .chan_advance_o (chan_advance_w),
        .frame_done_o   (frame_done_o),
        .current_state_o(fsm_state_w)
    );

    // ------------------------------------------------------------------------
    // Step 3: Block RAM State Storage Instance (Restores & Stores Channel State)
    // ------------------------------------------------------------------------
    pmu_channel_state_t bram_din;
    pmu_channel_state_t bram_dout;

    pmu_state_bram #(
        .DEPTH(MAX_CHANNELS),
        .ADDR_WIDTH(CHANNEL_BITS)
    ) u_state_bram (
        .clk  (clk),
        .rst_n(rst_n),
        .we   (bram_we_w),
        .addr (chan_ptr_q),
        .din  (bram_din),
        .dout (bram_dout)
    );

    // ------------------------------------------------------------------------
    // Step 4: Mahalanobis Distance Engine Instance
    // Computes D^2 = r^T * W * r
    // ------------------------------------------------------------------------
    q15_t dm2_val_w;
    logic mahal_alert_w;

    mahalanobis_matrix_engine #(
        .N(N)
    ) u_mahal_engine (
        .clk          (clk),
        .rst_n        (rst_n),
        .start_en     (mahal_start_w),
        .r_vec_in     (residual_vec_q),
        .w_matrix_in  (w_matrix_i),
        .thresh_t2_in (thresh_t2_i),
        .dm2_out      (dm2_val_w),
        .mahal_alert_o(mahal_alert_w),
        .done_o       (mahal_done_w)
    );

    // ------------------------------------------------------------------------
    // Step 5: Two-Sided CUSUM Filter Instance
    // Evaluates S^+ and S^- for the active channel using residual_vec_q[chan_ptr_q]
    // ------------------------------------------------------------------------
    q15_t s_pos_updated_w;
    q15_t s_neg_updated_w;
    logic cusum_pos_alert_w;
    logic cusum_neg_alert_w;
    logic cusum_alert_w;

    cusum_filter_q15 u_cusum_filter (
        .clk          (clk),
        .rst_n        (rst_n),
        .sample_valid (cusum_en_w),
        .e_in         (residual_vec_q[chan_ptr_q]),
        .param_k      (cusum_k_i),
        .param_h      (cusum_h_i),
        .param_nu0    (cusum_nu0_i),
        .s_pos_in     (bram_dout.s_pos),
        .s_neg_in     (bram_dout.s_neg),
        .s_pos_out    (s_pos_updated_w),
        .s_neg_out    (s_neg_updated_w),
        .alert_pos_o  (cusum_pos_alert_w),
        .alert_neg_o  (cusum_neg_alert_w),
        .alert_cusum_o(cusum_alert_w)
    );

    // ------------------------------------------------------------------------
    // Step 6: Decision Logic & BRAM State Assembly
    // ------------------------------------------------------------------------
    logic combined_fdi_alert_w;
    assign combined_fdi_alert_w = mahal_alert_w || cusum_alert_w;

    always_comb begin
        bram_din.s_pos          = s_pos_updated_w;
        bram_din.s_neg          = s_neg_updated_w;
        bram_din.last_sample    = raw_sample_q[chan_ptr_q];
        bram_din.spatial_alert  = mahal_alert_w;
        bram_din.temporal_alert = cusum_alert_w;
        bram_din.fdi_alert      = combined_fdi_alert_w;
        bram_din.alert_count    = combined_fdi_alert_w ? (bram_dout.alert_count + 1'b1) : bram_dout.alert_count;
    end

    // Registered Alert Outputs
    logic fdi_alert_reg;
    logic spatial_alert_reg;
    logic cusum_pos_reg;
    logic cusum_neg_reg;
    q15_t dm2_reg;
    q15_t s_pos_reg;
    q15_t s_neg_reg;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            fdi_alert_reg     <= 1'b0;
            spatial_alert_reg <= 1'b0;
            cusum_pos_reg     <= 1'b0;
            cusum_neg_reg     <= 1'b0;
            dm2_reg           <= Q15_ZERO;
            s_pos_reg         <= Q15_ZERO;
            s_neg_reg         <= Q15_ZERO;
        end else if (decision_en_w) begin
            fdi_alert_reg     <= combined_fdi_alert_w;
            spatial_alert_reg <= mahal_alert_w;
            cusum_pos_reg     <= cusum_pos_alert_w;
            cusum_neg_reg     <= cusum_neg_alert_w;
            dm2_reg           <= dm2_val_w;
            s_pos_reg         <= s_pos_updated_w;
            s_neg_reg         <= s_neg_updated_w;
        end
    end

    // Continuous Port Assignments
    assign fdi_alert_o       = fdi_alert_reg;
    assign spatial_alert_o   = spatial_alert_reg;
    assign cusum_pos_alert_o = cusum_pos_reg;
    assign cusum_neg_alert_o = cusum_neg_reg;
    assign dm2_metric_o      = dm2_reg;
    assign cusum_s_pos_o     = s_pos_reg;
    assign cusum_s_neg_o     = s_neg_reg;
    assign channel_active_o  = chan_ptr_q;

endmodule

