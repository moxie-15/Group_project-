// ============================================================================
// File: pmu_anomaly_engine_all_in_one.sv
// Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
// Standard: SystemVerilog IEEE 1800-2017
// Description: ALL-IN-ONE SELF-CONTAINED SINGLE RTL FILE.
//              Contains the package definition (fdi_pkg) and all submodules
//              in exact compilation order. Zero package dependency issues,
//              zero compile order headaches in Vivado.
//              Simply add this ONE file into Vivado Design Sources!
// ============================================================================

`timescale 1ns / 1ps

// ============================================================================
// PART 1: GLOBAL PACKAGE DEFINITION (fdi_pkg)
// ============================================================================
package fdi_pkg;

    parameter int N_CHANNELS      = 4;   // 4-dimensional PMU measurement vector
    parameter int MAX_CHANNELS    = 8;   // Scalable up to 8 channels in BRAM
    parameter int CHANNEL_BITS    = 3;   // clog2(MAX_CHANNELS)

    parameter int Q15_WIDTH       = 16;
    parameter int Q15_FRAC        = 15;
    parameter int Q15_ONE         = 16'sh7FFF; // +0.999969 (~1.0)
    parameter int Q15_ZERO        = 16'sh0000; // 0.0
    parameter int Q15_MINUS_ONE   = 16'sh8000; // -1.0

    parameter int PROD_WIDTH      = 32;
    parameter int PROD_FRAC       = 30;
    parameter int ACCUM_GUARD     = 2;
    parameter int ACCUM_WIDTH     = PROD_WIDTH + ACCUM_GUARD; // 34-bit

    typedef logic signed [Q15_WIDTH-1:0]    q15_t;
    typedef logic signed [PROD_WIDTH-1:0]   prod_q2_30_t;
    typedef logic signed [ACCUM_WIDTH-1:0]  accum_q4_30_t;

    typedef q15_t [N_CHANNELS-1:0]                 pmu_vec_t;
    typedef q15_t [N_CHANNELS-1:0][N_CHANNELS-1:0] pmu_mat_t;

    typedef struct packed {
        q15_t        s_pos;
        q15_t        s_neg;
        q15_t        last_sample;
        logic        spatial_alert;
        logic        temporal_alert;
        logic        fdi_alert;
        logic [9:0]  alert_count;
    } pmu_channel_state_t;

    typedef enum logic [2:0] {
        FSM_IDLE         = 3'b000,
        FSM_CAPTURE      = 3'b001,
        FSM_PREPROCESS   = 3'b010,
        FSM_MAHALANOBIS  = 3'b011,
        FSM_CUSUM        = 3'b100,
        FSM_DECISION     = 3'b101,
        FSM_STORE_RESULT = 3'b110,
        FSM_NEXT_CHANNEL = 3'b111
    } fsm_state_t;

    function automatic q15_t q15_mult(input q15_t a, input q15_t b);
        logic signed [31:0] full_prod;
        logic signed [31:0] rounded_prod;
        q15_t result;
        full_prod = logic signed [31:0]'(a) * logic signed [31:0]'(b);
        if (a == 16'sh8000 && b == 16'sh8000) begin
            result = 16'sh7FFF;
        end else begin
            rounded_prod = full_prod + 32'sh0000_4000;
            result = rounded_prod[30:15];
        end
        return result;
    endfunction

    function automatic q15_t q15_add_sat(input q15_t a, input q15_t b);
        logic signed [16:0] sum;
        q15_t result;
        sum = logic signed [16:0]'(a) + logic signed [16:0]'(b);
        if (sum > 17'sh07FFF) result = 16'sh7FFF;
        else if (sum < -17'sh08000) result = 16'sh8000;
        else result = sum[15:0];
        return result;
    endfunction

    function automatic q15_t q15_sub_sat(input q15_t a, input q15_t b);
        logic signed [16:0] diff;
        q15_t result;
        diff = logic signed [16:0]'(a) - logic signed [16:0]'(b);
        if (diff > 17'sh07FFF) result = 16'sh7FFF;
        else if (diff < -17'sh08000) result = 16'sh8000;
        else result = diff[15:0];
        return result;
    endfunction

endpackage: fdi_pkg

import fdi_pkg::*;

// ============================================================================
// PART 2: SIGNED FIXED-POINT MULTIPLIER (fixed_point_multiplier)
// ============================================================================
module fixed_point_multiplier (
    input  logic              clk,
    input  logic              rst_n,
    input  logic              en,
    input  q15_t              a_in,
    input  q15_t              b_in,
    output q15_t              p_out,
    output prod_q2_30_t       p_full_out,
    output logic              overflow_out
);
    logic signed [31:0] full_prod_q;
    logic signed [31:0] rounded_prod;
    logic               overflow_q;
    q15_t               p_reg;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            full_prod_q  <= '0;
            overflow_q   <= 1'b0;
            p_reg        <= '0;
        end else if (en) begin
            full_prod_q <= logic signed [31:0]'(a_in) * logic signed [31:0]'(b_in);
            if (a_in == 16'sh8000 && b_in == 16'sh8000) begin
                overflow_q <= 1'b1;
                p_reg      <= 16'sh7FFF;
            end else begin
                overflow_q <= 1'b0;
                rounded_prod = (logic signed [31:0]'(a_in) * logic signed [31:0]'(b_in)) + 32'sh0000_4000;
                p_reg <= rounded_prod[30:15];
            end
        end
    end

    assign p_out        = p_reg;
    assign p_full_out   = full_prod_q;
    assign overflow_out = overflow_q;
endmodule

// ============================================================================
// PART 3: GUARDED FIXED-POINT ACCUMULATOR (fixed_point_accumulator)
// ============================================================================
module fixed_point_accumulator #(
    parameter int IN_WIDTH   = PROD_WIDTH,
    parameter int ACC_WIDTH  = ACCUM_WIDTH,
    parameter int GUARD_BITS = ACCUM_GUARD
)(
    input  logic                   clk,
    input  logic                   rst_n,
    input  logic                   clear,
    input  logic                   en,
    input  logic signed [IN_WIDTH-1:0]  data_in,
    output logic signed [ACC_WIDTH-1:0] acc_out,
    output q15_t                   q15_out,
    output logic                   overflow_out
);
    logic signed [ACC_WIDTH-1:0] acc_reg;
    logic                        overflow_reg;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            acc_reg      <= '0;
            overflow_reg <= 1'b0;
        end else if (clear) begin
            acc_reg      <= '0;
            overflow_reg <= 1'b0;
        end else if (en) begin
            acc_reg <= acc_reg + logic signed [ACC_WIDTH-1:0]'(data_in);
            if ((acc_reg[33] == 1'b0 && |acc_reg[32:30]) ||
                (acc_reg[33] == 1'b1 && !(&acc_reg[32:30]))) begin
                overflow_reg <= 1'b1;
            end else begin
                overflow_reg <= 1'b0;
            end
        end
    end

    q15_t extracted_q15;
    always_comb begin
        logic signed [ACC_WIDTH-1:0] rounded_acc;
        rounded_acc = acc_reg + (1 << 14);
        if (rounded_acc[ACC_WIDTH-1] == 1'b0 && |rounded_acc[ACC_WIDTH-2:Q15_FRAC+15]) begin
            extracted_q15 = 16'sh7FFF;
        end else if (rounded_acc[ACC_WIDTH-1] == 1'b1 && !(&rounded_acc[ACC_WIDTH-2:Q15_FRAC+15])) begin
            extracted_q15 = 16'sh8000;
        end else begin
            extracted_q15 = rounded_acc[Q15_FRAC+14:15];
        end
    end

    assign acc_out      = acc_reg;
    assign q15_out      = extracted_q15;
    assign overflow_out = overflow_reg;
endmodule

// ============================================================================
// PART 4: TWO-SIDED CUSUM DETECTOR (cusum_filter_q15)
// ============================================================================
module cusum_filter_q15 (
    input  logic              clk,
    input  logic              rst_n,
    input  logic              sample_valid,
    input  q15_t              e_in,
    input  q15_t              param_k,
    input  q15_t              param_h,
    input  q15_t              param_nu0,
    input  q15_t              s_pos_in,
    input  q15_t              s_neg_in,
    output q15_t              s_pos_out,
    output q15_t              s_neg_out,
    output logic              alert_pos_o,
    output logic              alert_neg_o,
    output logic              alert_cusum_o
);
    logic signed [17:0] term_pos;
    logic signed [17:0] term_neg;
    logic signed [17:0] next_s_pos;
    logic signed [17:0] next_s_neg;

    q15_t s_pos_reg;
    q15_t s_neg_reg;
    logic alert_pos_reg;
    logic alert_neg_reg;

    always_comb begin
        term_pos   = logic signed [17:0]'(e_in) - logic signed [17:0]'(param_nu0) - logic signed [17:0]'(param_k);
        next_s_pos = logic signed [17:0]'(s_pos_in) + term_pos;
        term_neg   = logic signed [17:0]'(param_nu0) - logic signed [17:0]'(e_in) - logic signed [17:0]'(param_k);
        next_s_neg = logic signed [17:0]'(s_neg_in) + term_neg;
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s_pos_reg     <= Q15_ZERO;
            s_neg_reg     <= Q15_ZERO;
            alert_pos_reg <= 1'b0;
            alert_neg_reg <= 1'b0;
        end else if (sample_valid) begin
            if (next_s_pos <= 18'sh00000) begin
                s_pos_reg <= Q15_ZERO;
            end else if (next_s_pos >= 18'sh07FFF) begin
                s_pos_reg <= 16'sh7FFF;
            end else begin
                s_pos_reg <= next_s_pos[15:0];
            end

            if (next_s_neg <= 18'sh00000) begin
                s_neg_reg <= Q15_ZERO;
            end else if (next_s_neg >= 18'sh07FFF) begin
                s_neg_reg <= 16'sh7FFF;
            end else begin
                s_neg_reg <= next_s_neg[15:0];
            end

            alert_pos_reg <= (next_s_pos > logic signed [17:0]'(param_h));
            alert_neg_reg <= (next_s_neg > logic signed [17:0]'(param_h));
        end
    end

    assign s_pos_out       = s_pos_reg;
    assign s_neg_out       = s_neg_reg;
    assign alert_pos_o     = alert_pos_reg;
    assign alert_neg_o     = alert_neg_reg;
    assign alert_cusum_o   = alert_pos_reg || alert_neg_reg;
endmodule

// ============================================================================
// PART 5: MAHALANOBIS DISTANCE ENGINE (mahalanobis_matrix_engine)
// ============================================================================
module mahalanobis_matrix_engine #(
    parameter int N = N_CHANNELS
)(
    input  logic              clk,
    input  logic              rst_n,
    input  logic              start_en,
    input  pmu_vec_t          r_vec_in,
    input  pmu_mat_t          w_matrix_in,
    input  q15_t              thresh_t2_in,
    output q15_t              dm2_out,
    output logic              mahal_alert_o,
    output logic              done_o
);
    typedef enum logic [1:0] {
        M_IDLE  = 2'b00,
        M_MVM   = 2'b01,
        M_DOT   = 2'b10,
        M_DONE  = 2'b11
    } mahal_fsm_t;

    mahal_fsm_t state_q;
    pmu_vec_t r_latched;
    pmu_vec_t y_vec;
    q15_t     dm2_reg;
    logic     alert_reg;
    logic     done_reg;

    logic signed [33:0] mvm_row_acc [N];
    logic signed [31:0] mvm_prod    [N][N];

    always_comb begin
        for (int i = 0; i < N; i++) begin
            mvm_row_acc[i] = '0;
            for (int j = 0; j < N; j++) begin
                mvm_prod[i][j] = logic signed [31:0]'(w_matrix_in[i][j]) * logic signed [31:0]'(r_latched[j]);
                mvm_row_acc[i] = mvm_row_acc[i] + logic signed [33:0]'(mvm_prod[i][j]);
            end
        end
    end

    logic signed [33:0] dot_acc;
    logic signed [31:0] dot_prod [N];

    always_comb begin
        dot_acc = '0;
        for (int i = 0; i < N; i++) begin
            dot_prod[i] = logic signed [31:0]'(r_latched[i]) * logic signed [31:0]'(y_vec[i]);
            dot_acc     = dot_acc + logic signed [33:0]'(dot_prod[i]);
        end
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state_q   <= M_IDLE;
            r_latched <= '0;
            y_vec     <= '0;
            dm2_reg   <= Q15_ZERO;
            alert_reg <= 1'b0;
            done_reg  <= 1'b0;
        end else begin
            case (state_q)
                M_IDLE: begin
                    done_reg <= 1'b0;
                    if (start_en) begin
                        r_latched <= r_vec_in;
                        state_q   <= M_MVM;
                    end
                end

                M_MVM: begin
                    for (int i = 0; i < N; i++) begin
                        logic signed [33:0] rounded_row;
                        rounded_row = mvm_row_acc[i] + 34'sh0000_4000;
                        if (rounded_row > 34'sh003FFF_FFFF) begin
                            y_vec[i] <= 16'sh7FFF;
                        end else if (rounded_row < -34'sh004000_0000) begin
                            y_vec[i] <= 16'sh8000;
                        end else begin
                            y_vec[i] <= rounded_row[30:15];
                        end
                    end
                    state_q <= M_DOT;
                end

                M_DOT: begin
                    logic signed [33:0] rounded_dot;
                    rounded_dot = dot_acc + 34'sh0000_4000;
                    if (rounded_dot < 0) begin
                        dm2_reg <= Q15_ZERO;
                    end else if (rounded_dot > 34'sh003FFF_FFFF) begin
                        dm2_reg <= 16'sh7FFF;
                    end else begin
                        dm2_reg <= rounded_dot[30:15];
                    end
                    alert_reg <= (rounded_dot[30:15] > thresh_t2_in);
                    done_reg  <= 1'b1;
                    state_q   <= M_DONE;
                end

                M_DONE: begin
                    done_reg <= 1'b0;
                    state_q  <= M_IDLE;
                end

                default: state_q <= M_IDLE;
            endcase
        end
    end

    assign dm2_out       = dm2_reg;
    assign mahal_alert_o = alert_reg;
    assign done_o        = done_reg;
endmodule

// ============================================================================
// PART 6: ON-CHIP BLOCK RAM STORAGE (pmu_state_bram)
// ============================================================================
module pmu_state_bram #(
    parameter int DEPTH        = MAX_CHANNELS,
    parameter int ADDR_WIDTH   = CHANNEL_BITS,
    parameter int STATE_WIDTH  = $bits(pmu_channel_state_t)
)(
    input  logic                   clk,
    input  logic                   rst_n,
    input  logic                   we,
    input  logic [ADDR_WIDTH-1:0]  addr,
    input  pmu_channel_state_t     din,
    output pmu_channel_state_t     dout
);
    (* ram_style = "block" *) logic [STATE_WIDTH-1:0] ram_block [DEPTH];
    logic [STATE_WIDTH-1:0] dout_reg;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            dout_reg <= '0;
            for (int i = 0; i < DEPTH; i++) begin
                ram_block[i] <= '0;
            end
        end else begin
            if (we) begin
                ram_block[addr] <= din;
            end
            dout_reg <= ram_block[addr];
        end
    end

    assign dout = pmu_channel_state_t'(dout_reg);
endmodule

// ============================================================================
// PART 7: THREE-PROCESS MOORE FSM CONTROLLER (pmu_fsm_ctrl)
// ============================================================================
module pmu_fsm_ctrl (
    input  logic              clk,
    input  logic              rst_n,
    input  logic              data_valid,
    output logic              data_ready,
    input  logic              mahal_done,
    input  logic              channel_last,
    output logic              latch_sample_o,
    output logic              preprocess_en_o,
    output logic              mahal_start_o,
    output logic              cusum_en_o,
    output logic              decision_en_o,
    output logic              bram_we_o,
    output logic              chan_advance_o,
    output logic              frame_done_o,
    output fsm_state_t        current_state_o
);
    fsm_state_t current_state, next_state;

    // Process 1: Sequential State Register
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_state <= FSM_IDLE;
        end else begin
            current_state <= next_state;
        end
    end

    // Process 2: Combinational Next-State Logic
    always_comb begin
        next_state = current_state;
        case (current_state)
            FSM_IDLE: begin
                if (data_valid) next_state = FSM_CAPTURE;
                else            next_state = FSM_IDLE;
            end
            FSM_CAPTURE:      next_state = FSM_PREPROCESS;
            FSM_PREPROCESS:   next_state = FSM_MAHALANOBIS;
            FSM_MAHALANOBIS: begin
                if (mahal_done) next_state = FSM_CUSUM;
                else            next_state = FSM_MAHALANOBIS;
            end
            FSM_CUSUM:        next_state = FSM_DECISION;
            FSM_DECISION:     next_state = FSM_STORE_RESULT;
            FSM_STORE_RESULT: next_state = FSM_NEXT_CHANNEL;
            FSM_NEXT_CHANNEL: begin
                if (channel_last) next_state = FSM_IDLE;
                else              next_state = FSM_CAPTURE;
            end
            default:          next_state = FSM_IDLE;
        endcase
    end

    // Process 3: Pure Moore Combinational Output Logic
    always_comb begin
        data_ready      = 1'b0;
        latch_sample_o  = 1'b0;
        preprocess_en_o = 1'b0;
        mahal_start_o   = 1'b0;
        cusum_en_o      = 1'b0;
        decision_en_o   = 1'b0;
        bram_we_o       = 1'b0;
        chan_advance_o  = 1'b0;
        frame_done_o    = 1'b0;

        case (current_state)
            FSM_IDLE:         data_ready      = 1'b1;
            FSM_CAPTURE:      latch_sample_o  = 1'b1;
            FSM_PREPROCESS:   preprocess_en_o = 1'b1;
            FSM_MAHALANOBIS:  mahal_start_o   = 1'b1;
            FSM_CUSUM:        cusum_en_o      = 1'b1;
            FSM_DECISION:     decision_en_o   = 1'b1;
            FSM_STORE_RESULT: bram_we_o       = 1'b1;
            FSM_NEXT_CHANNEL: begin
                chan_advance_o = 1'b1;
                frame_done_o   = 1'b1;
            end
            default: ;
        endcase
    end

    assign current_state_o = current_state;
endmodule

// ============================================================================
// PART 8: TOP-LEVEL INTEGRATION ENTITY (pmu_anomaly_top)
// ============================================================================
module pmu_anomaly_top #(
    parameter int N = N_CHANNELS
)(
    input  logic              clk,
    input  logic              rst_n,

    input  logic              data_valid,
    output logic              data_ready,
    input  pmu_vec_t          pmu_sample_i,
    input  logic [CHANNEL_BITS-1:0] channel_id_i,

    input  pmu_vec_t          mu_vec_i,
    input  pmu_vec_t          sigma_inv_i,
    input  pmu_mat_t          w_matrix_i,
    input  q15_t              thresh_t2_i,
    input  q15_t              cusum_k_i,
    input  q15_t              cusum_h_i,
    input  q15_t              cusum_nu0_i,

    output logic              fdi_alert_o,
    output logic              spatial_alert_o,
    output logic              cusum_pos_alert_o,
    output logic              cusum_neg_alert_o,
    output q15_t              dm2_metric_o,
    output q15_t              cusum_s_pos_o,
    output q15_t              cusum_s_neg_o,
    output logic              frame_done_o,
    output logic [CHANNEL_BITS-1:0] channel_active_o
);

    logic latch_sample_w;
    logic preprocess_en_w;
    logic mahal_start_w;
    logic cusum_en_w;
    logic decision_en_w;
    logic bram_we_w;
    logic chan_advance_w;
    logic mahal_done_w;
    fsm_state_t fsm_state_w;

    logic [CHANNEL_BITS-1:0] chan_ptr_q;
    logic chan_last_w;

    assign chan_last_w = (chan_ptr_q == logic [CHANNEL_BITS-1:0]'(N - 1));

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            chan_ptr_q <= '0;
        end else if (chan_advance_w) begin
            if (chan_last_w) chan_ptr_q <= '0;
            else             chan_ptr_q <= chan_ptr_q + 1'b1;
        end
    end

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
                    residual_vec_q[i] <= q15_mult(diff, sigma_inv_i[i]);
                end
            end
        end
    end

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

    assign fdi_alert_o       = fdi_alert_reg;
    assign spatial_alert_o   = spatial_alert_reg;
    assign cusum_pos_alert_o = cusum_pos_reg;
    assign cusum_neg_alert_o = cusum_neg_reg;
    assign dm2_metric_o      = dm2_reg;
    assign cusum_s_pos_o     = s_pos_reg;
    assign cusum_s_neg_o     = s_neg_reg;
    assign channel_active_o  = chan_ptr_q;

endmodule
