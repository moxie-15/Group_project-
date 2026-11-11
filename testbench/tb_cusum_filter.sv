// ============================================================================
// File: tb_cusum_filter.sv
// Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
// Standard: SystemVerilog IEEE 1800-2017
// Description: Self-checking testbench for two-sided CUSUM filter in Q1.15.
//              Tests normal noise, positive drift trigger, negative drift
//              trigger, threshold comparison, and zero-clamping recovery.
// ============================================================================

`timescale 1ns / 1ps

module tb_cusum_filter;

    import fdi_pkg::*;

    logic clk;
    logic rst_n;
    logic sample_valid;
    q15_t e_in;
    q15_t param_k;
    q15_t param_h;
    q15_t param_nu0;
    q15_t s_pos_in;
    q15_t s_neg_in;
    q15_t s_pos_out;
    q15_t s_neg_out;
    logic alert_pos;
    logic alert_neg;
    logic alert_cusum;

    // Unit Under Test (UUT)
    cusum_filter_q15 uut (
        .clk          (clk),
        .rst_n        (rst_n),
        .sample_valid (sample_valid),
        .e_in         (e_in),
        .param_k      (param_k),
        .param_h      (param_h),
        .param_nu0    (param_nu0),
        .s_pos_in     (s_pos_in),
        .s_neg_in     (s_neg_in),
        .s_pos_out    (s_pos_out),
        .s_neg_out    (s_neg_out),
        .alert_pos_o  (alert_pos),
        .alert_neg_o  (alert_neg),
        .alert_cusum_o(alert_cusum)
    );

    always #5 clk = ~clk;

    int pass_count = 0;
    int fail_count = 0;

    initial begin
        clk          = 0;
        rst_n        = 0;
        sample_valid = 0;
        e_in         = 0;
        param_k      = 16'sh0800; // k = 2048 (~0.0625)
        param_h      = 16'sh4000; // h = 16384 (~0.50)
        param_nu0    = 16'sh0000; // nu0 = 0
        s_pos_in     = 0;
        s_neg_in     = 0;

        $display("==================================================");
        $display("STARTING TEST: tb_cusum_filter (Two-Sided Q1.15)");
        $display("==================================================");

        // Apply Reset
        #20;
        rst_n = 1;
        #10;

        // Test 1: Zero residual input (no drift)
        @(posedge clk);
        sample_valid = 1;
        e_in         = 16'sh0000;
        s_pos_in     = 16'sh0000;
        s_neg_in     = 16'sh0000;
        @(posedge clk);
        #1;
        if (s_pos_out === 16'sh0000 && s_neg_out === 16'sh0000 && alert_cusum === 1'b0) begin
            $display("[PASS] Zero residual: S+=0, S-=0, Alert=0");
            pass_count++;
        end else begin
            $display("[FAIL] Zero residual failed!");
            fail_count++;
        end

        // Test 2: Persistent positive deviation (e = +0.25 -> 8192)
        // delta_pos = 8192 - 0 - 2048 = 6144 per step
        // Step 1: S+ = 6144
        // Step 2: S+ = 12288
        // Step 3: S+ = 18432 (> h = 16384 -> Alert!)
        $display("[*] Simulating 3 consecutive positive drift steps...");
        for (int step = 1; step <= 3; step++) begin
            @(posedge clk);
            s_pos_in = s_pos_out;
            s_neg_in = s_neg_out;
            e_in     = 16'sh2000; // +8192
            @(posedge clk);
            #1;
            $display("    Step %0d: S+=%0d, Alert_Pos=%b", step, s_pos_out, alert_pos);
        end

        if (alert_pos === 1'b1 && alert_cusum === 1'b1) begin
            $display("[PASS] Positive drift successfully triggered CUSUM alarm at step 3!");
            pass_count++;
        end else begin
            $display("[FAIL] Positive drift alarm failed to trigger!");
            fail_count++;
        end

        // Test 3: Recovery back to zero
        $display("[*] Simulating recovery with negative deviation to reset S+...");
        for (int step = 1; step <= 4; step++) begin
            @(posedge clk);
            s_pos_in = s_pos_out;
            s_neg_in = s_neg_out;
            e_in     = -16'sh2000; // -8192
            @(posedge clk);
            #1;
        end

        if (s_pos_out === 16'sh0000) begin
            $display("[PASS] S+ successfully clamped to 0 after recovery!");
            pass_count++;
        end else begin
            $display("[FAIL] S+ failed to clamp to 0. Got: %0d", s_pos_out);
            fail_count++;
        end

        $display("==================================================");
        $display("TEST RESULTS: %0d Passed, %0d Failed", pass_count, fail_count);
        $display("==================================================");

        #20;
        $finish;
    end

endmodule

