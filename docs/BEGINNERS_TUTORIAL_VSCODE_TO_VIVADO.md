# Beginner's Guide: Connecting Vivado from VS Code & Python Dataflow
## Group 9: Smart Grid FDI Anomaly Detection Engine

Welcome! This guide is written specifically for you and your group members. It explains in simple terms:
1. **The Big Picture:** How Python, SystemVerilog, and Vivado connect and talk to each other.
2. **How to run Vivado directly from VS Code** (Terminal commands and GUI launch).
3. **Step-by-step workflow** to run the complete project from start to finish.

---

## 1. The Big Picture: How Everything Connects

Think of the project as a **3-step relay race**:

```
+---------------------------------------------------------------------------------------+
|  STEP 1: PYTHON                                                                       |
|  - generate_telemetry.py simulates power grid PMU sensors (IEEE 14-bus test feeder).  |
|  - It injects cyber-attacks (abrupt voltage spikes, slow power drifts).               |
|  - It saves everything into a spreadsheet file: data/pmu_telemetry.csv                |
+-------------------------------------------+-------------------------------------------+
                                            |
                                            v (Reads CSV file)
+---------------------------------------------------------------------------------------+
|  STEP 2: SYSTEMVERILOG HARDWARE (IN VIVADO)                                           |
|  - Vivado is the FPGA software. It tests our digital chip design (pmu_anomaly_top.sv).|
|  - The testbench (tb_pmu_anomaly_top.sv) reads data/pmu_telemetry.csv line-by-line.  |
|  - It pumps those measurements through our hardware math engine (Mahalanobis + CUSUM).|
|  - When it spots an attack, it raises the hardware FDI_ALERT alarm.                   |
|  - It logs what the hardware did into: sim/results/rtl_simulation_output.csv          |
+-------------------------------------------+-------------------------------------------+
                                            |
                                            v (Reads CSV results)
+---------------------------------------------------------------------------------------+
|  STEP 3: PYTHON EVALUATION & PLOTS                                                    |
|  - evaluate.py compares the hardware alarm against the true attack labels.            |
|  - plots.py draws 6 beautiful graphs showing the attacks and alarms in results/.       |
+---------------------------------------------------------------------------------------+
```

---

## 2. What is VS Code vs. What is Vivado?

- **VS Code:** This is your **Editor & Command Center**. You write code here, edit files, and use the built-in Terminal to run Python scripts or trigger Vivado commands.
- **Vivado:** This is AMD/Xilinx's **FPGA Development Tool**. It takes your SystemVerilog hardware code (`.sv`) and:
  1. Simulates it on your computer (draws digital waveform timelines like an oscilloscope).
  2. Synthesizes it (translates your code into real hardware logic gates, multipliers, and RAM).
  3. Checks timing (makes sure electrical signals travel fast enough across the chip).

---

## 3. How to Connect Vivado from VS Code

You can control Vivado directly from inside VS Code using the **VS Code Terminal**!

### Step 0: Open the Terminal in VS Code
In VS Code, press:
- **`Ctrl + ~`** (or go to top menu: **Terminal $\to$ New Terminal**).

### Step 1: Tell VS Code where Vivado is installed
If typing `vivado -version` in your terminal says *command not found*, that means Windows doesn't know where Vivado is yet.

On the group member's computer who has Vivado installed, run **ONE** of these commands in PowerShell depending on their Vivado version:

```powershell
# For Vivado 2023.2:
$env:Path += ";C:\Xilinx\Vivado\2023.2\bin"

# For Vivado 2022.2:
$env:Path += ";C:\Xilinx\Vivado\2022.2\bin"

# For Vivado 2020.2:
$env:Path += ";C:\Xilinx\Vivado\2020.2\bin"
```

To test that VS Code can talk to Vivado, type:
```powershell
vivado -version
```
If it prints `Vivado v202X.X...`, **you are connected!**

---

## 4. The 3 Easy Steps to Run Vivado from VS Code

We created **automatic script files (`.tcl`)** so you do NOT have to create projects manually by clicking hundreds of menus. You just type 1 line in the VS Code terminal!

### Step 1: Create the Vivado Project
In your VS Code terminal, run:
```powershell
vivado -mode batch -source scripts/create_project.tcl
```
*What this does:* Vivado automatically opens behind the scenes, loads all our `.sv` hardware files, links the timing constraints, and creates the ready-to-use project file at `vivado/project/fdi_anomaly_engine.xpr`.

---

### Step 2: Open Vivado in Graphical (GUI) Mode from VS Code
Once the project is created, you can launch the full Vivado window directly from your VS Code terminal:
```powershell
vivado vivado/project/fdi_anomaly_engine.xpr
```
*The full graphical Vivado window will pop open on your screen!*

---

### Step 3: What to Click in Vivado (For Your Report)

Inside the Vivado window, look at the **left sidebar** (called the **Flow Navigator**):

```
+-----------------------------------+
| FLOW NAVIGATOR                    |
|                                   |
| 1. SIMULATION                     |
|    └─► Click: "Run Simulation"    |  <-- Watch the digital waveforms!
|                                   |
| 2. SYNTHESIS                      |
|    └─► Click: "Run Synthesis"     |  <-- Generates BRAM & DSP slice report!
|                                   |
| 3. IMPLEMENTATION                 |
|    └─► Click: "Run Implementation"|  <-- Checks timing slack and Fmax!
+-----------------------------------+
```

1. **To see the wave signals:** Click **Run Simulation $\to$ Run Behavioral Simulation**. 
   - A waveform window opens showing clock signals, channel inputs, and the red `fdi_alert_o` signal jumping to `1` when an attack happens! Take a screenshot of this for your report.
2. **To get your Hardware Utilization Report:** Click **Run Synthesis**. 
   - When finished, click **View Report**. It shows:
     - How many **DSPs** were used (typically 4 to 8 multipliers).
     - How many **BRAMs** were used (our channel memory).
     - How many **LUTs & Flip-Flops** were used.
3. **To get your Clock Speed ($F_{\max}$):** Click **Run Implementation**.
   - Look at the **Timing Summary**:
     - Worst Negative Slack (WNS) should be $\ge 0$ (meaning timing PASSED!).

---

## 5. How Python Works With It (Run this on any computer!)

You don't even need Vivado to test and demonstrate the complete detection engine! The Python software pipeline simulates the exact same math:

In your VS Code Terminal, run these 4 commands in order:

```powershell
# 1. Generate the power grid sensor data and attacks:
python python/generate_telemetry.py

# 2. Run the bit-accurate hardware math model:
python python/golden_model.py

# 3. Print the accuracy, recall, and detection speed table:
python python/evaluate.py

# 4. Generate all 6 graphical plots for your presentation:
python python/plots.py
```

### Where are the outputs?
- Look inside the **`results/`** folder!
- You will find 6 ready-to-use PNG images:
  - `pmu_telemetry_attacks.png`: Shows normal power flow vs attacks.
  - `mahalanobis_vs_threshold.png`: Shows the distance jumping over the threshold.
  - `cusum_vs_threshold.png`: Shows the slow drift detection.
  - `fdi_alert_timeline.png`: Shows the hardware alarms firing.
  - `roc_curve.png`: Proves our design is superior to older methods.
  - `latency_cdf.png`: Shows detection speed.

You can paste these images directly into your PowerPoint slides and report!

