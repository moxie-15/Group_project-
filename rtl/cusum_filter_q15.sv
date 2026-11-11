// ============================================================================
// File: cusum_filter_q15.sv
// Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
// Standard: SystemVerilog IEEE 1800-2017
// Description: Two-Sided CUSUM (Cumulative Sum) Statistical Filter in Q1.15.
//              - S^+_n = max(0, S^+_{n-1} + (e - nu0 - k))
//              - S^-_n = max(0, S^-_{n-1} - (e - nu0 + k))
//              Time-multiplexed state restoration from BRAM and real-time alert.
// ============================================================================

`timescale 1ns / 1ps

module cusum_filter_q15
    import fdi_pkg::*;
(
    input  logic              clk,
    input  logic              rst_n,
    input  logic              sample_valid,   // Single-cycle enable from FSM

    // Current measurement / residual input in Q1.15
    input  q15_t              e_in,

    // Configurable CUSUM parameters (Q1.15)
    input  q15_t              param_k,        // Slack / reference allowance (e.g. 0.05 ~ 1638)
    input  q15_t              param_h,        // Decision threshold (e.g. 0.50 ~ 16384)
    input  q15_t              param_nu0,      // Nominal baseline mean (e.g. 0.0 for residual)

    // BRAM State Input (Restored for the active channel)
    input  q15_t              s_pos_in,
    input  q15_t              s_neg_in,

    // BRAM State Output (Updated for write-back)
    output q15_t              s_pos_out,
    output q15_t              s_neg_out,

    // Real-Time Alert Flags
    output logic              alert_pos_o,
    output logic              alert_neg_o,
    output logic              alert_cusum_o
);

    // Intermediate 18-bit signed math to prevent wrap-around before max(0, .)
    logic signed [17:0] term_pos;
    logic signed [17:0] term_neg;
    logic signed [17:0] next_s_pos;
    logic signed [17:0] next_s_neg;

    q15_t s_pos_reg;
    q15_t s_neg_reg;
    logic alert_pos_reg;
    logic alert_neg_reg;

    always_comb begin
        // Deviation terms:
        // term_pos = e - nu0 - k
        term_pos   = logic signed [17:0]'(e_in) - logic signed [17:0]'(param_nu0) - logic signed [17:0]'(param_k);
        next_s_pos = logic signed [17:0]'(s_pos_in) + term_pos;

        // term_neg = -(e - nu0 + k) = -e + nu0 - k
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
            // ----------------------------------------------------------------
            // 1. Positive CUSUM Accumulator: max(0, next_s_pos) with saturation
            // ----------------------------------------------------------------
            if (next_s_pos <= 18'sh00000) begin
                s_pos_reg <= Q15_ZERO;
            end else if (next_s_pos >= 18'sh07FFF) begin
                s_pos_reg <= 16'sh7FFF; // Positive saturation (+0.999969)
            end else begin
                s_pos_reg <= next_s_pos[15:0];
            end

            // ----------------------------------------------------------------
            // 2. Negative CUSUM Accumulator: max(0, next_s_neg) with saturation
            // ----------------------------------------------------------------
            if (next_s_neg <= 18'sh00000) begin
                s_neg_reg <= Q15_ZERO;
            end else if (next_s_neg >= 18'sh07FFF) begin
                s_neg_reg <= 16'sh7FFF; // Positive saturation
            end else begin
                s_neg_reg <= next_s_neg[15:0];
            end

            // ----------------------------------------------------------------
            // 3. Threshold Evaluation
            // ----------------------------------------------------------------
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

