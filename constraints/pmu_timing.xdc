# ==============================================================================
# File: pmu_timing.xdc
# Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
# Description: Timing and Clock Constraints for Synthesis & Implementation
# ==============================================================================

# ------------------------------------------------------------------------------
# Primary Clock Definition: 100 MHz (10.0 ns Period)
# Adjustable if group targets 50 MHz, 125 MHz, or 200 MHz
# ------------------------------------------------------------------------------
create_clock -period 10.000 -name clk -waveform {0.000 5.000} [get_ports clk]

# ------------------------------------------------------------------------------
# Input / Output Virtual Delays (assuming 2.0 ns external setup/hold budget)
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
set_output_delay -clock [get_clocks clk] -max 2.000 [get_ports frame_done_o]
set_output_delay -clock [get_clocks clk] -min 0.500 [get_ports frame_done_o]

# ------------------------------------------------------------------------------
# Asynchronous Reset False Path
# ------------------------------------------------------------------------------
set_false_path -from [get_ports rst_n]

