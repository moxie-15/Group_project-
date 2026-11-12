# ==============================================================================
# File: run_ac701_implementation.tcl
# Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
# Description: Tcl script to import AC701 constraints into an active project,
#              run synthesis/implementation, and generate timing reports.
# Usage in Vivado Tcl Console: source scripts/run_ac701_implementation.tcl
# Or batch mode: vivado -mode batch -source scripts/run_ac701_implementation.tcl
# ==============================================================================

puts "=========================================================================="
puts "  STARTING AC701 IMPLEMENTATION & TIMING CLOSURE FLOW"
puts "=========================================================================="

# 1. Add AC701 Timing Constraints if not already present
set xdc_file "constraints/ac701_timing.xdc"
if {[file exists $xdc_file]} {
    set existing_constrs [get_files -quiet -filter {FILE_TYPE == "XDC"}]
    if {[llength $existing_constrs] == 0} {
        puts "[*] Adding $xdc_file to constrs_1..."
        add_files -fileset constrs_1 -norecurse $xdc_file
    } else {
        puts "[*] Constraints already present: $existing_constrs"
    }
} else {
    puts "[WARN] $xdc_file not found in working directory."
}

# 2. Reset and Run Synthesis with Constraints
puts "[*] Launching Synthesis (synth_1)..."
reset_run synth_1
launch_runs synth_1 -jobs 4
wait_on_run synth_1

if {[get_property PROGRESS [get_runs synth_1]] != "100%"} {
    puts "[ERROR] Synthesis failed. Check synth_1 run log."
    return
}
puts "[+] Synthesis completed successfully."

# 3. Launch Implementation (Place & Route)
puts "[*] Launching Implementation (impl_1)..."
reset_run impl_1
launch_runs impl_1 -to_step route_design -jobs 4
wait_on_run impl_1

if {[get_property PROGRESS [get_runs impl_1]] != "100%"} {
    puts "[ERROR] Implementation failed. Check impl_1 run log."
    return
}
puts "[+] Implementation (Place & Route) completed successfully."

# 4. Open Implemented Design and Export Reports
open_run impl_1
file mkdir "vivado/reports"

puts "[*] Generating AC701 Post-Route Timing and Resource Reports..."
report_timing_summary -delay_type min_max -report_unconstrained -max_paths 10 -file "vivado/reports/ac701_timing_summary.rpt"
report_utilization -file "vivado/reports/ac701_utilization.rpt" -pb "vivado/reports/ac701_utilization.pb"
report_power -file "vivado/reports/ac701_power.rpt"

puts "=========================================================================="
puts "  AC701 IMPLEMENTATION RUN COMPLETED!"
puts "  Check reports in: vivado/reports/"
puts "    - Timing & Slack: vivado/reports/ac701_timing_summary.rpt"
puts "    - Resources:      vivado/reports/ac701_utilization.rpt"
puts "    - Power:          vivado/reports/ac701_power.rpt"
puts "=========================================================================="

