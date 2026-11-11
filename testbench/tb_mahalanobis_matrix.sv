// ============================================================================
// File: tb_mahalanobis_matrix.sv
// Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
// Standard: SystemVerilog IEEE 1800-2017
// Description: Self-checking testbench for Mahalanobis Distance Engine in Q1.15.
//              Tests matrix-vector multiplication y = W * r, quadratic dot
//              product D^2 = r^T * y, and threshold comparator alert.
// ============================================================================

`timescale 1ns / 1ps

module tb_mahalanobis_matrix;

    import fdi_pkg::*;

    logic clk;
    logic rst_n;
    logic start_en;
    pmu_vec_t r_vec_in;
    pmu_mat_t w_matrix_in;
    q15_t thresh_t2_in;
    q15_t dm2_out;
    logic mahal_alert;
    logic done;

    // Unit Under Test (UUT)
    mahalanobis_matrix_engine #(
        .N(N_CHANNELS)
    ) uut (
        .clk          (clk),
        .rst_n        (rst_n),
        .start_en     (start_en),
        .r_vec_in     (r_vec_in),
        .w_matrix_in  (w_matrix_in),
        .thresh_t2_in (thresh_t2_in),
        .dm2_out      (dm2_out),
        .mahal_alert_o(mahal_alert),
        .done_o       (done)
    );

    always #5 clk = ~clk;

    int pass_count = 0;
    int fail_count = 0;

    initial begin
        clk          = 0;
        rst_n        = 0;
        start_en     = 0;
        r_vec_in     = '{default: 16'sh0000};
        thresh_t2_in = 16'sh0A28; // 2600 in Q1.15

        // Calibrated 4x4 precision matrix diagonal dominant (symmetric positive definite)
        // Scaled into Q1.15
        w_matrix_in[0] = '{16'sh2000, 16'sh0800, -16'sh0400, 16'sh0000};
        w_matrix_in[1] = '{16'sh0800, 16'sh2400,  16'sh0200, -16'sh0400};
        w_matrix_in[2] = '{-16'sh0400, 16'sh0200, 16'sh2200,  16'sh0600};
        w_matrix_in[3] = '{16'sh0000, -16'sh0400, 16'sh0600,  16'sh2000};

        $display("==================================================");
        $display("STARTING TEST: tb_mahalanobis_matrix (Q1.15)");
        $display("==================================================");

        #20;
        rst_n = 1;
        #10;

        // Test 1: Zero residual vector -> D^2 must be 0
        @(posedge clk);
        start_en = 1;
        r_vec_in = '{default: 16'sh0000};
        @(posedge clk);
        start_en = 0;

        // Wait for done strobe
        wait(done == 1'b1);
        @(posedge clk);
        #1;
        if (dm2_out === 16'sh0000 && mahal_alert === 1'b0) begin
            $display("[PASS] Zero residual: D^2 = %0d, Alert = %b", dm2_out, mahal_alert);
            pass_count++;
        end else begin
            $display("[FAIL] Zero residual: Expected D^2=0, Got=%0d", dm2_out);
            fail_count++;
        end

        #20;

        // Test 2: Normal small residual vector -> D^2 should be small (< T^2)
        @(posedge clk);
        start_en = 1;
        r_vec_in[0] = 16'sh0400; // ~0.03
        r_vec_in[1] = 16'sh0300;
        r_vec_in[2] = -16'sh0200;
        r_vec_in[3] = 16'sh0100;
        @(posedge clk);
        start_en = 0;

        wait(done == 1'b1);
        @(posedge clk);
        #1;
        if (dm2_out < thresh_t2_in && mahal_alert === 1'b0) begin
            $display("[PASS] Small residual: D^2 = %0d (< %0d), Alert = 0", dm2_out, thresh_t2_in);
            pass_count++;
        end else begin
            $display("[FAIL] Small residual failed: D^2=%0d", dm2_out);
            fail_count++;
        end

        #20;

        // Test 3: Large attack anomaly vector -> D^2 should be large (> T^2 -> Alert!)
        @(posedge clk);
        start_en = 1;
        r_vec_in[0] = 16'sh4000; // +0.50
        r_vec_in[1] = 16'sh5000; // +0.625
        r_vec_in[2] = 16'sh3000;
        r_vec_in[3] = -16'sh4000;
        @(posedge clk);
        start_en = 0;

        wait(done == 1'b1);
        @(posedge clk);
        #1;
        if (dm2_out > thresh_t2_in && mahal_alert === 1'b1) begin
            $display("[PASS] Attack anomaly: D^2 = %0d (> %0d), Alert = 1", dm2_out, thresh_t2_in);
            pass_count++;
        end else begin
            $display("[FAIL] Attack anomaly failed to trigger alert: D^2=%0d", dm2_out);
            fail_count++;
        end

        $display("==================================================");
        $display("TEST RESULTS: %0d Passed, %0d Failed", pass_count, fail_count);
        $display("==================================================");

        #20;
        $finish;
    end

endmodule
