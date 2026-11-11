# ==============================================================================
# File: run_synthesis.tcl
# Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
# Description: Automated Synthesis Script. Runs RTL elaboration and synthesis,
#              generates detailed resource utilization (LUTs, FFs, DSPs, BRAMs)
#              and timing reports.
# Usage: vivado -mode batch -source scripts/run_synthesis.tcl
# ==============================================================================

set PROJ_DIR  "vivado/project"
set PROJ_NAME "fdi_anomaly_engine"
set REPORT_DIR "vivado/reports"

file mkdir $REPORT_DIR

# Open Vivado Project
open_project "$PROJ_DIR/$PROJ_NAME.xpr"

puts "=========================================================================="
puts "  RUNNING RTL ELABORATION & SYNTHESIS..."
puts "=========================================================================="

# Reset existing synthesis runs
reset_run synth_1

# Launch Synthesis with max jobs
launch_runs synth_1 -jobs 4
wait_on_run synth_1

# Check Synthesis Status
if {[get_property PROGRESS [get_runs synth_1]] != "100%"} {
    puts "\[ERROR\] Synthesis failed! Check synth_1 log files."
    exit 1
}

# Open Synthesized Design in Memory
open_run synth_1 -name synth_1

# ------------------------------------------------------------------------------
# Generate Comprehensive Resource & Timing Reports
# ------------------------------------------------------------------------------
puts "  Exporting Post-Synthesis Utilization & Timing Reports..."

# Overall Utilization
report_utilization -file "$REPORT_DIR/utilization_synth.rpt" -pb "$REPORT_DIR/utilization_synth.pb"

# Dedicated DSP and BRAM Reports
report_utilization -hierarchical -file "$REPORT_DIR/utilization_hierarchical_synth.rpt"

# Timing Summary (Setup Slack & Maximum Frequency)
report_timing_summary -delay_type max -report_unconstrained -check_timing_verbose -max_paths 10 -input_pins -routable_nets -file "$REPORT_DIR/timing_synth.rpt"

puts "=========================================================================="
puts "  SYNTHESIS COMPLETED SUCCESSFULLY!"
puts "  Reports generated in: $REPORT_DIR"
puts "    - Utilization: $REPORT_DIR/utilization_synth.rpt"
puts "    - Timing:      $REPORT_DIR/timing_synth.rpt"
puts "=========================================================================="

