# ==============================================================================
# File: run_implementation.tcl
# Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
# Description: Automated Implementation & Timing Closure Script.
#              Executes Place & Route (opt, place, phys_opt, route) and exports
#              post-route static timing, power, and final utilization metrics.
# Usage: vivado -mode batch -source scripts/run_implementation.tcl
# ==============================================================================

set PROJ_DIR   "vivado/project"
set PROJ_NAME  "fdi_anomaly_engine"
set REPORT_DIR "vivado/reports"

file mkdir $REPORT_DIR

open_project "$PROJ_DIR/$PROJ_NAME.xpr"

puts "=========================================================================="
puts "  RUNNING IMPLEMENTATION (PLACE & ROUTE)..."
puts "=========================================================================="

reset_run impl_1
launch_runs impl_1 -jobs 4
wait_on_run impl_1

if {[get_property PROGRESS [get_runs impl_1]] != "100%"} {
    puts "\[ERROR\] Implementation failed! Check impl_1 log files."
    exit 1
}

# Open Implemented Design
open_run impl_1

puts "  Exporting Post-Route Timing, Power & Utilization Reports..."

# Post-Route Timing (Critical for Setup/Hold Slack & Fmax)
report_timing_summary -delay_type min_max -report_unconstrained -check_timing_verbose -max_paths 10 -input_pins -routable_nets -file "$REPORT_DIR/timing_post_route.rpt"

# Post-Route Physical Resource Utilization
report_utilization -file "$REPORT_DIR/utilization_post_route.rpt" -pb "$REPORT_DIR/utilization_post_route.pb"

# Power Dissipation Estimate
report_power -file "$REPORT_DIR/power_post_route.rpt"

puts "=========================================================================="
puts "  IMPLEMENTATION COMPLETED!"
puts "  Check reports in $REPORT_DIR:"
puts "    - Timing & Slack:   $REPORT_DIR/timing_post_route.rpt"
puts "    - Final Resources:  $REPORT_DIR/utilization_post_route.rpt"
puts "    - Power Estimate:   $REPORT_DIR/power_post_route.rpt"
puts "=========================================================================="
