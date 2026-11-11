// ============================================================================
// File: pmu_state_bram.sv
// Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
// Standard: SystemVerilog IEEE 1800-2017
// Description: On-Chip Block RAM (BRAM) State Storage for PMU Channels.
//              Written following AMD/Xilinx recommended synchronous BRAM
//              inference style. Preserves per-channel CUSUM accumulators and
//              anomaly counters across time-multiplexed sample evaluations.
// ============================================================================

`timescale 1ns / 1ps

`ifndef FDI_PKG_SV
`include "fdi_pkg.sv"
`endif

import fdi_pkg::*;

module pmu_state_bram #(
    parameter int DEPTH        = MAX_CHANNELS,
    parameter int ADDR_WIDTH   = CHANNEL_BITS,
    parameter int STATE_WIDTH  = $bits(pmu_channel_state_t) // 61 bits
)(
    input  logic                   clk,
    input  logic                   rst_n,

    // Port A: Read/Write Access
    input  logic                   we,
    input  logic [ADDR_WIDTH-1:0]  addr,
    input  pmu_channel_state_t     din,
    output pmu_channel_state_t     dout
);

    // ------------------------------------------------------------------------
    // Block RAM Memory Array with Vivado Synthesis Attribute
    // ------------------------------------------------------------------------
    (* ram_style = "block" *) logic [STATE_WIDTH-1:0] ram_block [DEPTH];

    logic [STATE_WIDTH-1:0] dout_reg;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            dout_reg <= '0;
            // On reset, initialize states to 0
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
