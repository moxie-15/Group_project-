// ============================================================================
// File: fixed_point_multiplier.sv
// Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
// Standard: SystemVerilog IEEE 1800-2017
// Description: Pipelined Signed Q1.15 Fixed-Point Multiplier with full 32-bit
//              intermediate output, rounding, and saturation detection.
//              Infers AMD/Xilinx DSP48 slices cleanly.
// ============================================================================

`timescale 1ns / 1ps

`ifndef FDI_PKG_SV
`include "fdi_pkg.sv"
`endif

import fdi_pkg::*;

module fixed_point_multiplier (
    input  logic              clk,
    input  logic              rst_n,
    input  logic              en,

    // Operands in signed Q1.15 format
    input  q15_t              a_in,
    input  q15_t              b_in,

    // Outputs
    output q15_t              p_out,        // Saturated & rounded Q1.15 result
    output prod_q2_30_t       p_full_out,   // Raw 32-bit Q2.30 product
    output logic              overflow_out  // Asserted on (-1.0 * -1.0) saturation
);

    // Pipeline registers for high-frequency DSP mapping
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
            // 16-bit signed x 16-bit signed -> 32-bit signed (Q2.30)
            full_prod_q <= logic signed [31:0]'(a_in) * logic signed [31:0]'(b_in);

            // Handle corner case: -1.0 * -1.0 (0x8000 * 0x8000 = 0x40000000)
            if (a_in == 16'sh8000 && b_in == 16'sh8000) begin
                overflow_q <= 1'b1;
                p_reg      <= 16'sh7FFF; // Saturate to +0.999969
            end else begin
                overflow_q <= 1'b0;
                // Half-up rounding offset at bit 14
                rounded_prod = (logic signed [31:0]'(a_in) * logic signed [31:0]'(b_in)) + 32'sh0000_4000;
                // Extract Q1.15 bits [30:15]
                p_reg <= rounded_prod[30:15];
            end
        end
    end

    assign p_out        = p_reg;
    assign p_full_out   = full_prod_q;
    assign overflow_out = overflow_q;

endmodule
