// ============================================================================
// File: mahalanobis_matrix_engine.sv
// Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
// Standard: SystemVerilog IEEE 1800-2017
// Description: Synthesizable Q1.15 Mahalanobis Distance Engine for N=4 channels.
//              - Matrix-Vector Multiplication: y = W * r (where W = Sigma^-1)
//              - Quadratic Inner Product: D^2 = r^T * y
//              - Real-time threshold comparison D^2 > T^2
// ============================================================================

`timescale 1ns / 1ps

module mahalanobis_matrix_engine
    import fdi_pkg::*;
#(
    parameter int N = N_CHANNELS
)(
    input  logic              clk,
    input  logic              rst_n,
    input  logic              start_en,       // Start strobe from FSM

    // Input normalized residual vector r[0..3] in Q1.15
    input  pmu_vec_t          r_vec_in,

    // Configurable Inverse Covariance Matrix W = Sigma^-1 (Q1.15)
    input  pmu_mat_t          w_matrix_in,

    // Configurable Detection Threshold T^2 (Q1.15)
    input  q15_t              thresh_t2_in,

    // Outputs
    output q15_t              dm2_out,        // Computed squared Mahalanobis distance
    output logic              mahal_alert_o,  // Anomaly flag: D^2 > T^2
    output logic              done_o          // Completion strobe
);

    // ------------------------------------------------------------------------
    // Precision Matrix Multiplier Storage & Stage Registers
    // ------------------------------------------------------------------------
    typedef enum logic [1:0] {
        M_IDLE  = 2'b00,
        M_MVM   = 2'b01,  // Compute y = W * r
        M_DOT   = 2'b10,  // Compute D^2 = r^T * y
        M_DONE  = 2'b11
    } mahal_fsm_t;

    mahal_fsm_t state_q;

    pmu_vec_t r_latched;
    pmu_vec_t y_vec;
    q15_t     dm2_reg;
    logic     alert_reg;
    logic     done_reg;

    // ------------------------------------------------------------------------
    // MVM Combinatorial Dot-Products across Rows
    // Each row i: y[i] = sum_j (W[i][j] * r[j])
    // Full 32-bit products with 34-bit accumulation, then rounded to Q1.15
    // ------------------------------------------------------------------------
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

    // ------------------------------------------------------------------------
    // Quadratic Dot-Product: D^2 = sum_i (r[i] * y[i])
    // ------------------------------------------------------------------------
    logic signed [33:0] dot_acc;
    logic signed [31:0] dot_prod [N];

    always_comb begin
        dot_acc = '0;
        for (int i = 0; i < N; i++) begin
            dot_prod[i] = logic signed [31:0]'(r_latched[i]) * logic signed [31:0]'(y_vec[i]);
            dot_acc     = dot_acc + logic signed [33:0]'(dot_prod[i]);
        end
    end

    // ------------------------------------------------------------------------
    // Sequential State Controller
    // ------------------------------------------------------------------------
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
                    // Latch rounded Q1.15 elements of y
                    for (int i = 0; i < N; i++) begin
                        logic signed [33:0] rounded_row;
                        rounded_row = mvm_row_acc[i] + 34'sh0000_4000;
                        // Saturate if overflow
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
                    // Extract rounded & saturated D^2
                    logic signed [33:0] rounded_dot;
                    rounded_dot = dot_acc + 34'sh0000_4000;

                    // D^2 is strictly positive; clamp negative artifacts to 0
                    if (rounded_dot < 0) begin
                        dm2_reg <= Q15_ZERO;
                    end else if (rounded_dot > 34'sh003FFF_FFFF) begin
                        dm2_reg <= 16'sh7FFF; // Saturate
                    end else begin
                        dm2_reg <= rounded_dot[30:15];
                    end

                    // Evaluate spatial threshold
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

