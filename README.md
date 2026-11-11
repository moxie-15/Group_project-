# Group 9: Smart Grid False Data Injection (FDI) Anomaly Detection Engine

[![Language](https://img.shields.io/badge/Language-SystemVerilog%20%7C%20Python-blue.svg)](https://github.com/moxie-15/Group_project-)
[![Hardware-Target](https://img.shields.io/badge/Target-AMD%20Xilinx%20Vivado%20FPGA-orange.svg)](https://github.com/moxie-15/Group_project-)
[![Arithmetic](https://img.shields.io/badge/Format-Signed%20Q1.15%20Fixed--Point-green.svg)](https://github.com/moxie-15/Group_project-)
[![License](https://img.shields.io/badge/License-Academic%20Open-lightgrey.svg)](LICENSE)

An FPGA-based, hardware-accelerated **False Data Injection (FDI) Anomaly Detection Engine** designed to protect smart grid state estimators and Phasor Measurement Units (PMUs) against sophisticated cyber-attacks. Implemented in synthesizable SystemVerilog, verified with a bit-accurate Python golden reference model, and validated across physical IEEE 14-bus test feeder telemetry.

---

## 1. System Architecture & Detection Framework

Traditional power system Bad Data Detection (BDD) algorithms rely on static $L_2$-norm residual checks ($J(x) = \|z - H\hat{x}\| \le \tau$). Adversaries bypass static tests by injecting stealthy perturbation vectors $a = H c$. 

Our architecture implements a **Dual-Layer Hardware Detection Pipeline**:
1. **Layer 1 — Spatial Correlation (Mahalanobis Distance Engine):**
   $$D^2 = (x - \mu)^T \Sigma^{-1} (x - \mu) = r^T W r$$
   Computes quadratic distance against the empirical precision matrix $W = \Sigma^{-1}$. Identifies spatial correlation violations across multi-channel PMU streams in real time.
2. **Layer 2 — Temporal Drift (Two-Sided CUSUM Engine):**
   $$S^+(n) = \max\left(0, \, S^+(n-1) + e_n - \nu_0 - k\right)$$
   $$S^-(n) = \max\left(0, \, S^-(n-1) - (e_n - \nu_0 + k)\right)$$
   Recursively accumulates small persistent drifts that intentionally fly beneath the instantaneous threshold $T^2$.
3. **Combined Decision Logic:**
   $$\text{FDI\_ALERT} = (D^2 > T^2) \lor (S^+ > h) \lor (S^- > h)$$

```
                                  +------------------------------------+
                                  |        Configuration Registers     |
                                  |  T², h, k, ν₀, W (Σ⁻¹), μ, σ⁻¹     |
                                  +-----------------+------------------+
                                                    |
                                    Config Bus      v
+--------------------------+     +------------------------+     +-------------------------------------+
| Ingestion Interface      |     | Measurement            |     | Mahalanobis Distance Engine         |
| clk, rst_n               |     | Preprocessor           |     |                                     |
| data_valid / data_ready  |==>  | r[i] = (x[i]-μ[i])*σ⁻¹ |==>  | 1. MVM: y = W * r (Q1.15)           |
| x[0..3] (PMU Telemetry)  |     | Format: Signed Q1.15   |     | 2. Quadratic Dot: D² = rᵀ*y         |
+--------------------------+     +------------------------+     |    Format: Q1.15 with saturation    |
                                                                +------------------+------------------+
                                                                                   | D² (Q1.15)
                                                                                   v
+--------------------------+     +------------------------+     +-------------------------------------+
| Hardware Interrupt & Tele|     | Combined Decision      |     | Two-Sided CUSUM Detector            |
| - FDI_ALERT (IRQ)        |<==  | - Spatial: D² > T²     |<==  | S⁺(n) = max(0, S⁺(n-1)+e-ν₀-k)      |
| - SPATIAL_ALERT          |     | - Temporal: S⁺ > h     |     | S⁻(n) = max(0, S⁻(n-1)-(e-ν₀+k))    |
| - CUSUM_POS / NEG_ALERT  |     |             S⁻ > h     |     | Format: Q1.15 zero-clamped          |
+--------------------------+     +------------------------+     +-------------------------------------+
```

---

## 2. Key Hardware & Architectural Features

- **Signed Q1.15 Fixed-Point Datapath:** 16-bit signed arithmetic (1 sign, 15 fractional bits) representing $[-1.0, +0.999969]$. Multiplication utilizes 32-bit intermediate products (Q2.30), 34-bit accumulator guard bits, explicit convergent half-up rounding (`+ 0x4000`), and corner-case saturation ($-1.0 \times -1.0 \to +0.999969$).
- **Three-Process Moore FSM Controller:** Strict separation into:
  1. `always_ff` sequential state register with active-low asynchronous reset.
  2. `always_comb` combinational next-state transition logic.
  3. `always_comb` pure Moore combinational output logic (outputs depend solely on `current_state`).
- **On-Chip Block RAM (BRAM) State Storage:** `pmu_state_bram.sv` infers dedicated Xilinx Block RAM (`ram_style = "block"`), storing per-channel positive/negative CUSUM states and anomaly counters across time-multiplexed channels.
- **Microsecond Latency & High Throughput:** 9 clock cycles total latency ($90\text{ ns}$ at $100\text{ MHz}$) with 4 cycles throughput per 4-channel measurement vector ($25\text{ MSamples/sec}$).

---

## 3. Repository Directory Structure

```
Group_project/
├── rtl/                                  # Synthesizable SystemVerilog RTL modules
│   ├── fdi_pkg.sv                        # Architectural types, Q1.15 parameters & math helpers
│   ├── pmu_anomaly_top.sv                # Top-level entity integrating FSM, BRAM & engines
│   ├── cusum_filter_q15.sv               # Two-sided recursive Q1.15 CUSUM detector
│   ├── mahalanobis_matrix_engine.sv      # Matrix-vector & quadratic distance engine
│   ├── pmu_state_bram.sv                 # Vivado inferable on-chip BRAM channel storage
│   ├── pmu_fsm_ctrl.sv                   # Three-process Moore FSM state controller
│   ├── fixed_point_multiplier.sv         # Pipelined signed Q1.15 DSP multiplier slice
│   └── fixed_point_accumulator.sv        # Guarded signed fixed-point accumulator
├── testbench/                            # SystemVerilog simulation verification
│   ├── tb_pmu_anomaly_top.sv             # Top-level CSV-driven simulation testbench
│   ├── tb_cusum_filter.sv                # Standalone CUSUM self-checking testbench
│   ├── tb_mahalanobis_matrix.sv          # Standalone Mahalanobis self-checking testbench
│   └── tb_fixed_point_multiplier.sv      # Multiplier unit testbench
├── python/                               # Verification & telemetry pipeline
│   ├── generate_telemetry.py             # Generates physical IEEE 14-bus telemetry & attacks
│   ├── golden_model.py                   # Bit-accurate Q1.15 reference model
│   ├── evaluate.py                       # Performance metrics (Accuracy, F1, Latency)
│   └── plots.py                          # Publication-grade figures generator
├── data/                                 # Datasets & calibration parameters
│   ├── pmu_telemetry.csv                 # 1000-sample 4-channel dataset with attack labels
│   ├── golden_results.csv                # Bit-accurate golden model outputs
│   └── reference/
│       └── calibration_parameters.json   # Calibrated mean, cov, W, and thresholds
├── scripts/                              # Vivado automation Tcl scripts
│   ├── create_project.tcl                # Automated Vivado project generation
│   ├── run_synthesis.tcl                 # Elaboration & out-of-context synthesis
│   └── run_implementation.tcl            # Place & Route, timing closure, reports
├── constraints/                          # Timing and pin constraints
│   └── pmu_timing.xdc                    # 100 MHz clock & I/O timing constraints
├── docs/                                 # Engineering documentation
│   ├── architecture.md                   # Full hardware specification & latency budgets
│   ├── fixed_point_analysis.md           # Word-length proofs & dynamic range analysis
│   └── VIVADO_HANDOFF.md                 # Complete guide for group members running Vivado
├── results/                              # Generated verification figures & reports
│   ├── pmu_telemetry_attacks.png         # Telemetry profiles with shaded attack spans
│   ├── mahalanobis_vs_threshold.png      # D^2 vs spatial threshold T^2
│   ├── cusum_vs_threshold.png            # S+ and S- vs decision threshold h
│   ├── fdi_alert_timeline.png            # Interrupt flags vs ground-truth attack timeline
│   ├── roc_curve.png                     # ROC curve vs static baseline detector
│   ├── latency_cdf.png                   # Empirical detection latency CDF
│   └── evaluation_metrics.json           # Quantitative classification metrics report
└── README.md
```

---

## 4. Quantitative Performance Evaluation

Performance evaluated over 1,000 continuous smart grid telemetry samples incorporating:
1. **Scenario 1:** Abrupt False Voltage Injection on Bus 2 (Samples 200–350).
2. **Scenario 2:** Gradual Persistent Power Drift on Line 1–2 (Samples 500–700).
3. **Scenario 3:** Coordinated Stealthy Subspace Attack ($a = Hc$) designed to bypass static residual tests (Samples 800–921).

| Metric | Proposed Dual-Layer (MD + CUSUM) | Baseline (Mahalanobis Alone) | Baseline (CUSUM Alone) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | **87.70%** | 86.20% | 87.30% |
| **Precision** | **97.03%** | 98.83% | 98.04% |
| **Recall (Sensitivity)** | **76.22%** | 71.55% | 74.52% |
| **F1-Score** | **0.8537** | 0.8300 | 0.8468 |
| **False Positive Rate (FPR)** | **2.08%** | 0.76% | 1.32% |
| **False Negative Rate (FNR)** | **23.78%** | 28.45% | 25.48% |
| **Scenario 1 Latency (Abrupt FDI)** | **0 samples (Instantaneous)** | 0 samples | 0 samples |
| **Scenario 2 Latency (Gradual Drift)**| **76 samples** | 76 samples | 110 samples |
| **Scenario 3 Latency (Stealthy $a=Hc$)**| **0 samples (Instantaneous)** | 0 samples | 2 samples |

---

## 5. Quick-Start Execution Guide

### A. Reproducing the Python Pipeline
Requirements: Python 3.9+ with `numpy`, `scipy`, `pandas`, and `matplotlib`.
```bash
# 1. Generate IEEE 14-bus derived telemetry dataset
python python/generate_telemetry.py

# 2. Run bit-accurate Q1.15 golden reference model
python python/golden_model.py

# 3. Calculate quantitative evaluation metrics
python python/evaluate.py

# 4. Generate all 6 publication figures in results/
python python/plots.py
```

### B. Running Vivado Synthesis & Implementation (For Group Members)
Refer to [`docs/VIVADO_HANDOFF.md`](file:///c:/Users/MOXIE/Desktop/group_project/docs/VIVADO_HANDOFF.md) for full instructions:
```bash
# Step 1: Create project and import sources
vivado -mode batch -source scripts/create_project.tcl

# Step 2: Run synthesis and generate resource reports
vivado -mode batch -source scripts/run_synthesis.tcl

# Step 3: Run implementation and generate timing closure reports
vivado -mode batch -source scripts/run_implementation.tcl
```

---

## 6. Academic Attribution & Requirements Checklist

- [x] Complete Q1.15 arithmetic datapath with saturation and rounding.
- [x] Three-process Moore FSM controller with clean state assignments.
- [x] Dual-layer anomaly detection (Mahalanobis distance + Two-sided CUSUM).
- [x] On-chip Block RAM (BRAM) PMU state storage.
- [x] Time-multiplexed multi-channel support.
- [x] IEEE 14-bus test feeder power-flow telemetry and stealthy attack simulation.
- [x] Bit-accurate Python reference model.
- [x] Full evaluation metrics and publication figures (ROC curve, latency CDF, waveforms).
- [x] Automated Vivado Tcl scripts and handoff guide.
