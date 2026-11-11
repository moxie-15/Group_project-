// ============================================================================
// File: tb_fixed_point_multiplier.sv
// Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
// Standard: SystemVerilog IEEE 1800-2017
// Description: Self-checking testbench for signed Q1.15 fixed-point multiplier.
//              Tests normal multiplication, sign handling, rounding, LSB
//              precision, and corner-case saturation (-1.0 * -1.0).
// ============================================================================

`timescale 1ns / 1ps

module tb_fixed_point_multiplier;

    import fdi_pkg::*;

    logic clk;
    logic rst_n;
    logic en;
    q15_t a_in;
    q15_t b_in;
    q15_t p_out;
    prod_q2_30_t p_full_out;
    logic overflow_out;

    // Unit Under Test (UUT)
    fixed_point_multiplier uut (
        .clk         (clk),
        .rst_n       (rst_n),
        .en          (en),
        .a_in        (a_in),
        .b_in        (b_in),
        .p_out       (p_out),
        .p_full_out  (p_full_out),
        .overflow_out(overflow_out)
    );

    // Clock generation (100 MHz, 10ns period)
    always #5 clk = ~clk;

    int pass_count = 0;
    int fail_count = 0;

    task check_result(string test_name, q15_t expected_p, logic expected_ovf);
        @(posedge clk);
        #1; // Sample output after clock edge
        if (p_out === expected_p && overflow_out === expected_ovf) begin
            $display("[PASS] %s: a=%0d, b=%0d -> p=%0d, ovf=%b", 
                     test_name, a_in, b_in, p_out, overflow_out);
            pass_count++;
        end else begin
            $display("[FAIL] %s: a=%0d, b=%0d -> Expected p=%0d, Got=%0d; Expected ovf=%b, Got=%b", 
                     test_name, a_in, b_in, expected_p, p_out, expected_ovf, overflow_out);
            fail_count++;
        end
    endtask

    initial begin
        clk   = 0;
        rst_n = 0;
        en    = 0;
        a_in  = 0;
        b_in  = 0;

        $display("==================================================");
        $display("STARTING TEST: tb_fixed_point_multiplier (Q1.15)");
        $display("==================================================");

        // Apply Reset
        #20;
        rst_n = 1;
        en    = 1;
        #10;

        // Test 1: Zero multiplication (0.0 * 0.5 = 0.0)
        a_in = 16'sh0000; b_in = 16'sh4000;
        check_result("Zero Multiplication", 16'sh0000, 1'b0);

        // Test 2: Unity positive (0.5 * 0.5 = 0.25 -> 0x4000 * 0x4000 = 0x2000)
        a_in = 16'sh4000; b_in = 16'sh4000;
        check_result("0.5 * 0.5 = 0.25", 16'sh2000, 1'b0);

        // Test 3: Positive * Negative (0.5 * -0.5 = -0.25 -> 0x4000 * 0xC000 = 0xE000)
        a_in = 16'sh4000; b_in = 16'shC000;
        check_result("0.5 * -0.5 = -0.25", 16'shE000, 1'b0);

        // Test 4: Negative * Negative (-0.5 * -0.5 = +0.25)
        a_in = 16'shC000; b_in = 16'shC000;
        check_result("-0.5 * -0.5 = +0.25", 16'sh2000, 1'b0);

        // Test 5: Maximum positive operands (+0.9999 * +0.9999)
        // 0x7FFF * 0x7FFF = 0x3FFF_0001 + 0x4000 = 0x3FFF_4001 -> bits [30:15] = 0x7FFE
        a_in = 16'sh7FFF; b_in = 16'sh7FFF;
        check_result("Max Positive Mult", 16'sh7FFE, 1'b0);

        // Test 6: Corner case saturation: -1.0 * -1.0 (0x8000 * 0x8000 -> 0x7FFF with overflow flag)
        a_in = 16'sh8000; b_in = 16'sh8000;
        check_result("Corner Case: -1.0 * -1.0 Saturation", 16'sh7FFF, 1'b1);

        $display("==================================================");
        $display("TEST RESULTS: %0d Passed, %0d Failed", pass_count, fail_count);
        $display("==================================================");

        if (fail_count == 0) begin
            $display("[STATUS] FIXED_POINT_MULTIPLIER VERIFICATION SUCCESSFUL!");
        end else begin
            $display("[STATUS] TEST FAILED WITH %0d ERRORS!", fail_count);
        end

        #20;
        $finish;
    end

endmodule

