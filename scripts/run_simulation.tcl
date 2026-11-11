# ==============================================================================
# File: run_simulation.tcl
# Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
# Description: Automated Behavioral Simulation Script for Vivado XSim.
#              Compiles RTL and testbenches, runs behavioral simulation,
#              generates waveform database (.wdb/.vcd), and logs results.
# Usage: vivado -mode batch -source scripts/run_simulation.tcl
# ==============================================================================

set PROJ_DIR "vivado/project"
set PROJ_NAME "fdi_anomaly_engine"
set SIM_DIR  "sim"

file mkdir "$SIM_DIR/logs"
file mkdir "$SIM_DIR/waveforms"
file mkdir "$SIM_DIR/results"

open_project "$PROJ_DIR/$PROJ_NAME.xpr"

puts "=========================================================================="
puts "  RUNNING BEHAVIORAL SIMULATION: tb_pmu_anomaly_top"
puts "=========================================================================="

# Set simulation fileset properties
set_property top tb_pmu_anomaly_top [get_filesets sim_1]
set_property top_lib xil_defaultlib [get_filesets sim_1]

# Configure simulation settings to dump full waveforms
set_property -name {xsim.simulate.runtime} -value {all} -objects [get_filesets sim_1]
set_property -name {xsim.simulate.log_all_signals} -value {true} -objects [get_filesets sim_1]

# Launch behavioral simulation
launch_simulation -simset [get_filesets sim_1] -mode behavioral

puts "  Running simulation for 200 microseconds..."
run 200 us

# Export VCD waveform file for external waveform viewers (e.g. GTKWave)
write_vcd "$SIM_DIR/waveforms/pmu_anomaly_simulation.vcd"

puts "=========================================================================="
puts "  SIMULATION FINISHED!"
puts "  Waveform written to: $SIM_DIR/waveforms/pmu_anomaly_simulation.vcd"
puts "  Simulation outputs:  $SIM_DIR/results/rtl_simulation_output.csv"
puts "=========================================================================="

close_sim

