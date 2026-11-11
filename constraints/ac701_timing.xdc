# ==============================================================================
# File: ac701_timing.xdc
# Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
# Target Board: Xilinx AC701 Evaluation Kit (xc7a200tfbg676-2)
# Reference: AC701 Evaluation Board User Guide (UG952)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Primary Clock Definition
# The AC701 provides an on-board 200.000 MHz differential oscillator (SiT9102).
# For core IP evaluation, the single-ended internal clock 'clk' is constrained.
# 
# Option A (Recommended baseline): 100 MHz clock (10.0 ns period)
# Option B (Target stress test):   200 MHz clock (5.0 ns period)
# ------------------------------------------------------------------------------
create_clock -period 10.000 -name clk -waveform {0.000 5.000} [get_ports clk]

# ------------------------------------------------------------------------------
# 2. Asynchronous Reset Constraints
# Asynchronous active-low reset 'rst_n' is a false path for setup/hold timing.
# ------------------------------------------------------------------------------
set_false_path -from [get_ports rst_n]

# ------------------------------------------------------------------------------
# 3. Quasi-Static Configuration Parameters
# In power grid substation PMU edge-monitoring, baseline statistical parameters
# (mean, variance, precision matrix W, thresholds) are calibrated offline and
# remain static during continuous streaming. Treating them as quasi-static false
# paths prevents timing analysis distortion from massive 515-pin fan-out.
# ------------------------------------------------------------------------------
set_false_path -from [get_ports mu_vec_i*]
set_false_path -from [get_ports sigma_inv_i*]
set_false_path -from [get_ports w_matrix_i*]
set_false_path -from [get_ports thresh_t2_i*]
set_false_path -from [get_ports cusum_k_i*]
set_false_path -from [get_ports cusum_h_i*]
set_false_path -from [get_ports cusum_nu0_i*]
set_false_path -from [get_ports channel_id_i*]

# ------------------------------------------------------------------------------
# 4. Dynamic Ingestion & Anomaly Alert Stream Delays
# Realistic 20% setup / hold timing budget on active streaming signals.
# ------------------------------------------------------------------------------
set_input_delay -clock [get_clocks clk] -max 2.000 [get_ports data_valid]
set_input_delay -clock [get_clocks clk] -min 0.500 [get_ports data_valid]
set_input_delay -clock [get_clocks clk] -max 2.000 [get_ports pmu_sample_i*]
set_input_delay -clock [get_clocks clk] -min 0.500 [get_ports pmu_sample_i*]

set_output_delay -clock [get_clocks clk] -max 2.000 [get_ports data_ready]
set_output_delay -clock [get_clocks clk] -min 0.500 [get_ports data_ready]
set_output_delay -clock [get_clocks clk] -max 2.000 [get_ports fdi_alert_o]
set_output_delay -clock [get_clocks clk] -min 0.500 [get_ports fdi_alert_o]
set_output_delay -clock [get_clocks clk] -max 2.000 [get_ports spatial_alert_o]
set_output_delay -clock [get_clocks clk] -min 0.500 [get_ports spatial_alert_o]
set_output_delay -clock [get_clocks clk] -max 2.000 [get_ports cusum_pos_alert_o]
set_output_delay -clock [get_clocks clk] -min 0.500 [get_ports cusum_pos_alert_o]
set_output_delay -clock [get_clocks clk] -max 2.000 [get_ports cusum_neg_alert_o]
set_output_delay -clock [get_clocks clk] -min 0.500 [get_ports cusum_neg_alert_o]
set_output_delay -clock [get_clocks clk] -max 2.000 [get_ports frame_done_o]
set_output_delay -clock [get_clocks clk] -min 0.500 [get_ports frame_done_o]
set_output_delay -clock [get_clocks clk] -max 2.000 [get_ports dm2_metric_o*]
set_output_delay -clock [get_clocks clk] -min 0.500 [get_ports dm2_metric_o*]
set_output_delay -clock [get_clocks clk] -max 2.000 [get_ports cusum_s_pos_o*]
set_output_delay -clock [get_clocks clk] -min 0.500 [get_ports cusum_s_pos_o*]
set_output_delay -clock [get_clocks clk] -max 2.000 [get_ports cusum_s_neg_o*]
set_output_delay -clock [get_clocks clk] -min 0.500 [get_ports cusum_s_neg_o*]
set_output_delay -clock [get_clocks clk] -max 2.000 [get_ports channel_active_o*]
set_output_delay -clock [get_clocks clk] -min 0.500 [get_ports channel_active_o*]
