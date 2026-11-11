# ==============================================================================
# File: create_project.tcl
# Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
# Description: Automated Vivado Project Generation Script.
#              Creates project, adds RTL/TB sources, imports timing constraints,
#              and sets top-level entities for synthesis and simulation.
# Usage: vivado -mode batch -source scripts/create_project.tcl
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Configurable FPGA Target Part
# ------------------------------------------------------------------------------
# Group Members: Change this variable if your lab board uses a different FPGA!
# Common Boards:
#   - Digilent Basys 3 (Artix-7):   xc7a35tcpg236-1   (Default)
#   - Digilent Nexys A7 (Artix-7):  xc7a100tcsg324-1
#   - Digilent PYNQ-Z1 (Zynq-7000): xc7z020clg400-1
#   - Digilent Zybo Z7 (Zynq-7000): xc7z010clg400-1
set TARGET_PART "xc7a35tcpg236-1"

set PROJ_NAME "fdi_anomaly_engine"
set PROJ_DIR  "vivado/project"

puts "=========================================================================="
puts "  CREATING VIVADO PROJECT: $PROJ_NAME"
puts "  TARGET FPGA PART:       $TARGET_PART"
puts "=========================================================================="

# Create project directory
file mkdir $PROJ_DIR

# Create or overwrite project
create_project $PROJ_NAME $PROJ_DIR -part $TARGET_PART -force

# ------------------------------------------------------------------------------
# 2. Add SystemVerilog RTL Source Files
# ------------------------------------------------------------------------------
add_files -fileset sources_1 [list \
    "rtl/fdi_pkg.sv" \
    "rtl/fixed_point_multiplier.sv" \
    "rtl/fixed_point_accumulator.sv" \
    "rtl/cusum_filter_q15.sv" \
    "rtl/mahalanobis_matrix_engine.sv" \
    "rtl/pmu_state_bram.sv" \
    "rtl/pmu_fsm_ctrl.sv" \
    "rtl/pmu_anomaly_top.sv" \
]

# Set SystemVerilog file type explicitly
set_property file_type SystemVerilog [get_files -of_objects [get_filesets sources_1]]

# Set Top-Level Synthesis Module
set_property top pmu_anomaly_top [get_filesets sources_1]

# ------------------------------------------------------------------------------
# 3. Add Constraints
# ------------------------------------------------------------------------------
add_files -fileset constrs_1 -norecurse "constraints/pmu_timing.xdc"

# ------------------------------------------------------------------------------
# 4. Add Testbench Simulation Files
# ------------------------------------------------------------------------------
add_files -fileset sim_1 [list \
    "testbench/tb_pmu_anomaly_top.sv" \
    "testbench/tb_cusum_filter.sv" \
    "testbench/tb_mahalanobis_matrix.sv" \
    "testbench/tb_fixed_point_multiplier.sv" \
]

set_property file_type SystemVerilog [get_files -of_objects [get_filesets sim_1]]
set_property top tb_pmu_anomaly_top [get_filesets sim_1]

# Update Compile Order
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1

puts "=========================================================================="
puts "  PROJECT CREATED SUCCESSFULLY!"
puts "  To open project in GUI: vivado $PROJ_DIR/$PROJ_NAME.xpr"
puts "=========================================================================="
