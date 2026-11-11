// ============================================================================
// File: tb_pmu_anomaly_top.sv
// Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
// Standard: SystemVerilog IEEE 1800-2017
// Description: Comprehensive CSV-Driven SystemVerilog Testbench for the Top-Level
//              pmu_anomaly_top engine. Reads data/pmu_telemetry.csv, feeds samples
//              via the valid/ready handshake, logs real-time RTL detection flags,
//              and writes simulation results to sim/results/rtl_simulation_output.csv.
// ============================================================================

`timescale 1ns / 1ps

module tb_pmu_anomaly_top;

    import fdi_pkg::*;

    // Clock and Reset Signals
    logic clk;
    logic rst_n;

    // Ingestion Handshake
    logic data_valid;
    logic data_ready;
    pmu_vec_t pmu_sample_i;
    logic [CHANNEL_BITS-1:0] channel_id_i;

    // Configurable Reference Parameters
    pmu_vec_t mu_vec_i;
    pmu_vec_t sigma_inv_i;
    pmu_mat_t w_matrix_i;
    q15_t     thresh_t2_i;
    q15_t     cusum_k_i;
    q15_t     cusum_h_i;
    q15_t     cusum_nu0_i;

    // Real-Time Anomaly Outputs
    logic fdi_alert_o;
    logic spatial_alert_o;
    logic cusum_pos_alert_o;
    logic cusum_neg_alert_o;
    q15_t dm2_metric_o;
    q15_t cusum_s_pos_o;
    q15_t cusum_s_neg_o;
    logic frame_done_o;
    logic [CHANNEL_BITS-1:0] channel_active_o;

    // Unit Under Test (UUT)
    pmu_anomaly_top #(
        .N(N_CHANNELS)
    ) uut (
        .clk              (clk),
        .rst_n            (rst_n),
        .data_valid       (data_valid),
        .data_ready       (data_ready),
        .pmu_sample_i     (pmu_sample_i),
        .channel_id_i     (channel_id_i),
        .mu_vec_i         (mu_vec_i),
        .sigma_inv_i      (sigma_inv_i),
        .w_matrix_i       (w_matrix_i),
        .thresh_t2_i      (thresh_t2_i),
        .cusum_k_i        (cusum_k_i),
        .cusum_h_i        (cusum_h_i),
        .cusum_nu0_i      (cusum_nu0_i),
        .fdi_alert_o      (fdi_alert_o),
        .spatial_alert_o  (spatial_alert_o),
        .cusum_pos_alert_o(cusum_pos_alert_o),
        .cusum_neg_alert_o(cusum_neg_alert_o),
        .dm2_metric_o     (dm2_metric_o),
        .cusum_s_pos_o    (cusum_s_pos_o),
        .cusum_s_neg_o    (cusum_s_neg_o),
        .frame_done_o     (frame_done_o),
        .channel_active_o (channel_active_o)
    );

    // 100 MHz Clock Generation (10ns period)
    always #5 clk = ~clk;

    // File I/O Descriptors
    int in_file, out_file;
    string line;
    int sample_idx, ch0_val, ch1_val, ch2_val, ch3_val, attack_label;
    real v1, v2, p12, q12;
    string dummy_hex0, dummy_hex1, dummy_hex2, dummy_hex3, attack_type;

    int samples_processed = 0;
    int alerts_detected   = 0;
    int attacks_in_csv    = 0;

    initial begin
        clk          = 0;
        rst_n        = 0;
        data_valid   = 0;
        channel_id_i = '0;
        pmu_sample_i = '{default: 16'sh0000};

        // Calibrated baseline parameters
        mu_vec_i    = '{default: 16'sh0000}; // Pre-centered normalized data
        sigma_inv_i = '{default: 16'sh7FFF}; // Unity scaling in normalized space

        // 4x4 Precision Matrix from calibration
        w_matrix_i[0] = '{16'sh2000, 16'sh0800, -16'sh0400, 16'sh0000};
        w_matrix_i[1] = '{16'sh0800, 16'sh2400,  16'sh0200, -16'sh0400};
        w_matrix_i[2] = '{-16'sh0400, 16'sh0200, 16'sh2200,  16'sh0600};
        w_matrix_i[3] = '{16'sh0000, -16'sh0400, 16'sh0600,  16'sh2000};

        thresh_t2_i = 16'sh0A28; // 2600 in Q1.15
        cusum_k_i   = 16'sh1964; // 6500 in Q1.15
        cusum_h_i   = 16'sh55F0; // 22000 in Q1.15
        cusum_nu0_i = 16'sh0000; // 0.0

        $display("==================================================================");
        $display("STARTING TOP-LEVEL SIMULATION: tb_pmu_anomaly_top (CSV-Driven)");
        $display("==================================================================");

        // Reset Sequence
        #40;
        rst_n = 1;
        #20;

        // Open input CSV file
        in_file = $fopen("data/pmu_telemetry.csv", "r");
        if (in_file == 0) begin
            $display("[WARN] Could not open 'data/pmu_telemetry.csv'. Trying relative '../data/pmu_telemetry.csv'...");
            in_file = $fopen("../data/pmu_telemetry.csv", "r");
        end

        // Open output log file
        out_file = $fopen("sim/results/rtl_simulation_output.csv", "w");
        if (out_file == 0) begin
            out_file = $fopen("../sim/results/rtl_simulation_output.csv", "w");
        end

        if (out_file != 0) begin
            $fdisplay(out_file, "sample_idx,dm2_metric,spatial_alert,cusum_pos_alert,cusum_neg_alert,fdi_alert,ground_truth");
        end

        if (in_file != 0) begin
            $display("[*] Successfully opened telemetry CSV. Streaming measurement vectors...");
            // Discard header line
            void'($fgets(line, in_file));

            while (!$feof(in_file)) begin
                int n_fields;
                void'($fgets(line, in_file));
                if (line.len() > 5) begin
                    n_fields = $sscanf(line, "%d,%f,%f,%f,%f,%d,%d,%d,%d,%s,%s,%s,%s,%d,%s",
                                       sample_idx, v1, v2, p12, q12,
                                       ch0_val, ch1_val, ch2_val, ch3_val,
                                       dummy_hex0, dummy_hex1, dummy_hex2, dummy_hex3,
                                       attack_label, attack_type);

                    if (n_fields >= 14) begin
                        // Wait until DUT is ready to accept a new vector
                        while (!data_ready) @(posedge clk);

                        @(posedge clk);
                        data_valid      = 1'b1;
                        pmu_sample_i[0] = q15_t'(ch0_val);
                        pmu_sample_i[1] = q15_t'(ch1_val);
                        pmu_sample_i[2] = q15_t'(ch2_val);
                        pmu_sample_i[3] = q15_t'(ch3_val);

                        @(posedge clk);
                        data_valid = 1'b0;

                        // Wait for full frame evaluation across channels
                        wait(frame_done_o == 1'b1);
                        @(posedge clk);
                        #1;

                        samples_processed++;
                        if (fdi_alert_o) alerts_detected++;
                        if (attack_label == 1) attacks_in_csv++;

                        if (out_file != 0) begin
                            $fdisplay(out_file, "%0d,%0d,%0b,%0b,%0b,%0b,%0d",
                                      sample_idx, dm2_metric_o, spatial_alert_o,
                                      cusum_pos_alert_o, cusum_neg_alert_o,
                                      fdi_alert_o, attack_label);
                        end

                        if (samples_processed % 200 == 0) begin
                            $display("[*] Processed %0d samples... Current alerts: %0d", 
                                     samples_processed, alerts_detected);
                        end
                    end
                end
            end

            $fclose(in_file);
            if (out_file != 0) $fclose(out_file);
        end else begin
            $display("[WARN] CSV file not found in simulator path. Running built-in test vectors...");
            // Built-in automated vector tests (abrupt attack, drift, normal)
            for (int t = 0; t < 20; t++) begin
                while (!data_ready) @(posedge clk);
                @(posedge clk);
                data_valid = 1'b1;
                if (t >= 5 && t <= 10) begin
                    // Attack vector: high voltage anomaly on channel 1
                    pmu_sample_i[0] = 16'sh0200;
                    pmu_sample_i[1] = 16'sh6000; // Attack!
                    pmu_sample_i[2] = 16'sh0100;
                    pmu_sample_i[3] = -16'sh0200;
                end else begin
                    // Normal noise
                    pmu_sample_i[0] = 16'sh0100;
                    pmu_sample_i[1] = 16'sh0050;
                    pmu_sample_i[2] = -16'sh0100;
                    pmu_sample_i[3] = 16'sh0080;
                end

                @(posedge clk);
                data_valid = 1'b0;
                wait(frame_done_o == 1'b1);
                @(posedge clk);
                #1;
                samples_processed++;
                if (fdi_alert_o) alerts_detected++;
                $display("Sample %0d: D^2=%0d, S+=%0d, Alert=%b", t, dm2_metric_o, cusum_s_pos_o, fdi_alert_o);
            end
        end

        $display("==================================================================");
        $display("SIMULATION COMPLETE SUMMARY:");
        $display("  Total Samples Processed: %0d", samples_processed);
        $display("  Total Attacks Injected:  %0d", attacks_in_csv);
        $display("  Total FDI Alerts Fired:  %0d", alerts_detected);
        $display("==================================================================");

        #100;
        $finish;
    end

endmodule

