# Vivado Handoff & Hardware Verification Guide
## Smart Grid False Data Injection (FDI) Anomaly Engine
**Group 9 — Academic Digital Design Project**  
**Handoff Date:** November 2026  
**Target Tool:** AMD / Xilinx Vivado Design Suite (2020.2 or newer)  

---

## 1. Executive Handoff Summary

The complete synthesizable SystemVerilog RTL, testbenches, Python golden reference model, telemetry datasets, and automated Tcl automation scripts have been prepared and tested.

This document guides group members on:
1. Setting up and configuring the target FPGA device part.
2. Executing automated synthesis, implementation, and timing closure.
3. Extracting all hardware metrics (BRAM, DSP48, LUTs, FFs, setup/hold slack, $F_{\max}$, stream throughput) required for the final academic report and presentation.

> **CRITICAL ACADEMIC INTEGRITY NOTE:**  
> In accordance with digital design standards, do not invent timing or utilization numbers. Run the scripts on your machine with Vivado installed, open the generated reports in `vivado/reports/`, and record the exact physical numbers.

---

## 2. Setting Up the Target FPGA Part

Before executing Vivado scripts, confirm the exact FPGA device or development board available in your university laboratory.

Open [`scripts/create_project.tcl`](file:///c:/Users/MOXIE/Desktop/group_project/scripts/create_project.tcl) and set the `TARGET_PART` variable at Line 20:

```tcl
# Example Target Boards:
#   - Digilent Basys 3 (Artix-7):   set TARGET_PART "xc7a35tcpg236-1"
#   - Digilent Nexys A7 (Artix-7):  set TARGET_PART "xc7a100tcsg324-1"
#   - Digilent PYNQ-Z1 (Zynq-7000): set TARGET_PART "xc7z020clg400-1"
#   - Digilent Zybo Z7 (Zynq-7000): set TARGET_PART "xc7z010clg400-1"
set TARGET_PART "xc7a35tcpg236-1"
```

---

## 3. Running via Command Line (Automated Batch Mode)

Ensure `vivado` is available in your system `PATH` (e.g. from the Vivado Command Prompt or Terminal). From the root of the repository:

### Step 1: Create the Vivado Project
```bash
vivado -mode batch -source scripts/create_project.tcl
```
*Creates project file `vivado/project/fdi_anomaly_engine.xpr` and imports all RTL, TB, and XDC constraints.*

### Step 2: Run RTL Elaboration & Out-of-Context Synthesis
```bash
vivado -mode batch -source scripts/run_synthesis.tcl
```
*Generates post-synthesis utilization and timing reports in `vivado/reports/`.*

### Step 3: Run Place & Route (Implementation)
```bash
vivado -mode batch -source scripts/run_implementation.tcl
```
*Executes placement, physical optimization, routing, and generates post-route static timing and power reports.*

---

## 4. Running via Vivado Graphical Interface (GUI Mode)

1. Launch Vivado GUI.
2. In Vivado, click **Open Project** and browse to:
   `vivado/project/fdi_anomaly_engine.xpr`
3. In the Flow Navigator (left pane):
   - **Run Simulation:** Click `Run Simulation -> Run Behavioral Simulation`. Verify waveform transitions for `pmu_anomaly_top`.
   - **Run Synthesis:** Click `Run Synthesis`.
   - **Run Implementation:** Click `Run Implementation`.
   - **Generate Bitstream:** Click `Generate Bitstream` if targeting a physical laboratory board.

---

## 5. How to Extract Required Report Metrics

All output reports are automatically exported to `vivado/reports/`. Open these text files to retrieve the required data:

### A. BRAM (Block RAM) Utilization
- **Report File:** `vivado/reports/utilization_synth.rpt` or `utilization_post_route.rpt`
- **Section:** Look under **"Block RAM Tile"** or **"RAMB18E1 / RAMB36E1"**.
- **Verification Question:** *Did `pmu_state_bram.sv` infer dedicated Block RAM?*
  - Look for `ram_block_reg` in the hierarchical report (`utilization_hierarchical_synth.rpt`). Vivado will report $0.5$ or $1$ RAMB18 primitive used. If inferred as distributed RAM (LUTRAM), explain that the memory depth (8 channels $\times 61$ bits) is small enough for Vivado heuristics to prefer LUTs over BRAMs unless forced via `(* ram_style = "block" *)`.

### B. DSP48 Utilization
- **Report File:** `vivado/reports/utilization_synth.rpt`
- **Section:** Look under **"DSPs"** / **"DSP48E1"**.
- **Verification Question:** *Did Vivado infer hardware DSP multipliers for Q1.15 matrix multiplication?*
  - Note the count of active DSP slices (typically 4 to 8 DSP48E1s for the 4-channel MVM and quadratic dot product).

### C. Logic Utilization (LUTs and Flip-Flops)
- **Report File:** `vivado/reports/utilization_post_route.rpt`
- Record:
  - **Slice LUTs:** Total LUTs consumed and percentage of total device budget.
  - **Slice Registers (FFs):** Total Flip-Flops consumed.
  - **Occupied Slices:** Total physical slices used.

### D. Static Timing Analysis & Slacks
- **Report File:** `vivado/reports/timing_post_route.rpt`
- **Section:** Look under **"Design Timing Summary"**:
  - **Worst Negative Slack (WNS):** Represents Setup Timing Slack. Must be **$\ge 0\text{ ns}$** for timing closure.
  - **Total Negative Slack (TNS):** Must be **$0.000\text{ ns}$**.
  - **Worst Hold Slack (WHS):** Represents Hold Timing Slack. Must be **$\ge 0\text{ ns}$**.
  - **Total Hold Slack (THS):** Must be **$0.000\text{ ns}$**.

### E. Maximum Clock Frequency ($F_{\max}$) Calculation
Calculate the maximum safe clock frequency from the post-route WNS and target clock period ($T_{\text{clk}} = 10.0\text{ ns}$):
$$F_{\max} = \frac{1}{T_{\text{clk}} - \text{WNS}} = \frac{1}{10.0\text{ ns} - \text{WNS}}$$
*Example:* If $\text{WNS} = +4.2\text{ ns}$, then:
$$F_{\max} = \frac{1}{10.0\text{ ns} - 4.2\text{ ns}} = \frac{1}{5.8\text{ ns}} \approx 172.4\text{ MHz}$$

### F. Maximum Supported PMU Stream Capacity
Based on the Three-Process Moore FSM schedule (`pmu_fsm_ctrl.sv`):
- Time per 4-channel measurement frame: **4 clock cycles** throughput.
- Maximum input telemetry stream capacity:
$$\text{Capacity} = \frac{F_{\max}}{4\text{ cycles/sample}}$$
*Example:* At $100\text{ MHz}$, the engine processes:
$$\frac{100 \times 10^6}{4} = \mathbf{25\text{ Million samples/second}}$$
Since standard smart grid PMUs report at $30 - 60\text{ samples/second}$, the FPGA engine can concurrently monitor thousands of high-speed substations or PMU channels in real time.

---

## 6. Checklist for Group Members

Before final report submission:
- [ ] Pull latest commit from `main` branch.
- [ ] Run `python python/golden_model.py` and `python python/evaluate.py`.
- [ ] Verify that plots in `results/` are up to date.
- [ ] Run `scripts/create_project.tcl` with your board's `TARGET_PART`.
- [ ] Run `scripts/run_synthesis.tcl` and `scripts/run_implementation.tcl`.
- [ ] Copy exact numbers from `vivado/reports/` into the presentation slide deck / report.
- [ ] Attach waveform screenshot from Vivado Behavioral Simulation showing `fdi_alert_o` triggering on sample 200.
