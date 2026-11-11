// ============================================================================
// File: fixed_point_accumulator.sv
// Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
// Standard: SystemVerilog IEEE 1800-2017
// Description: Parameterized Guarded Fixed-Point Accumulator with synchronous
//              clear, saturation detection, and rounded Q1.15 extraction.
// ============================================================================

`timescale 1ns / 1ps

`ifndef FDI_PKG_SV
`include "fdi_pkg.sv"
`endif

import fdi_pkg::*;

module fixed_point_accumulator #(
    parameter int IN_WIDTH   = PROD_WIDTH,  // Default 32-bit input (Q2.30)
    parameter int ACC_WIDTH  = ACCUM_WIDTH, // Default 34-bit accumulator (Q4.30)
    parameter int GUARD_BITS = ACCUM_GUARD  // 2 guard bits for N=4 sum
)(
    input  logic                   clk,
    input  logic                   rst_n,
    input  logic                   clear,
    input  logic                   en,

    // Input operand (sign-extended internally)
    input  logic signed [IN_WIDTH-1:0]  data_in,

    // Wide full-precision accumulator output
    output logic signed [ACC_WIDTH-1:0] acc_out,

    // Saturated & rounded Q1.15 output
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
            // Sign-extended accumulation
            acc_reg <= acc_reg + logic signed [ACC_WIDTH-1:0]'(data_in);
            
            // Overflow occurs if magnitude exceeds representable Q1.15 range
            // In Q4.30 format, integer bits are [33:30].
            // If any of the top 3 bits differ from the sign bit, it exceeds Q1.15
            if ((acc_reg[33] == 1'b0 && |acc_reg[32:30]) ||
                (acc_reg[33] == 1'b1 && !(&acc_reg[32:30]))) begin
                overflow_reg <= 1'b1;
            end else begin
                overflow_reg <= 1'b0;
            end
        end
    end

    // Convert Q4.30 to Q1.15 with convergent rounding
    q15_t extracted_q15;
    always_comb begin
        logic signed [ACC_WIDTH-1:0] rounded_acc;
        // Add round bit at bit 14 of the fractional part (bit 14 of 30 fractional bits)
        rounded_acc = acc_reg + (1 << 14);

        if (rounded_acc[ACC_WIDTH-1] == 1'b0 && |rounded_acc[ACC_WIDTH-2:Q15_FRAC+15]) begin
            extracted_q15 = 16'sh7FFF; // Positive saturation
        end else if (rounded_acc[ACC_WIDTH-1] == 1'b1 && !(&rounded_acc[ACC_WIDTH-2:Q15_FRAC+15])) begin
            extracted_q15 = 16'sh8000; // Negative saturation
        end else begin
            extracted_q15 = rounded_acc[Q15_FRAC+14:15];
        end
    end

    assign acc_out      = acc_reg;
    assign q15_out      = extracted_q15;
    assign overflow_out = overflow_reg;

endmodule
