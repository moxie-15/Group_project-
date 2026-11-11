# Academic Final Project Report
## FPGA-Based Smart Grid False Data Injection (FDI) Anomaly Detection Engine Using Mahalanobis Distance and CUSUM

**Academic Group:** Group 9  
**Course / Subject:** Advanced Digital System Design & Power Systems Cyber-Security  
**Target Hardware:** AMD / Xilinx Vivado (Artix-7 / Zynq-7000 FPGA)  
**Implementation Standard:** Synthesizable SystemVerilog (IEEE 1800-2017) & Python 3  
**Repository:** [https://github.com/moxie-15/Group_project-](https://github.com/moxie-15/Group_project-)  

---

## Abstract

Modern electrical smart grids rely heavily on Phasor Measurement Units (PMUs) and Supervisory Control and Data Acquisition (SCADA) telemetry for real-time state estimation. However, state estimators are fundamentally vulnerable to stealthy False Data Injection (FDI) attacks, in which an adversary injects coordinated perturbation vectors $a = H c$ lying within the measurement Jacobian subspace, leaving conventional $L_2$-norm bad data residuals unchanged. 

This project designs, implements, and verifies an FPGA-accelerated, microsecond-latency **Dual-Layer FDI Anomaly Detection Engine** in synthesizable SystemVerilog. The architecture couples a **Spatial Correlation Layer** (Mahalanobis Distance $D^2 = r^T \Sigma^{-1} r$) with a **Temporal Trend Layer** (Two-Sided Cumulative Sum / CUSUM control charts). The datapath strictly executes in **signed 16-bit Q1.15 fixed-point arithmetic** with 32-bit intermediate products, guard-bit accumulation, convergent rounding, and corner-case saturation. Per-channel state persistence across multi-channel PMU streams is managed via **on-chip Block RAM (BRAM)** orchestrated by a canonical **Three-Process Moore Finite State Machine (FSM)**. 

Evaluated across 1,000 continuous telemetry frames derived from an IEEE 14-bus test feeder under three distinct cyber-attack scenarios (abrupt voltage manipulation, gradual power flow drift, and coordinated stealthy subspace attacks), the engine achieves **87.70% overall accuracy, 97.03% precision, an F1-score of 0.8537, and a False Positive Rate of only 2.08%**. Hardware pipeline latency is **90 ns (9 clock cycles at 100 MHz)**, yielding a peak stream processing capacity of **25 Million samples/second**—thousands of times faster than real-time wire speed.

---

## 1. Problem Formulation & Threat Model

### 1.1 Smart Grid State Estimation & Vulnerability
In a power transmission grid with $m$ measurements and $n$ state variables ($m > n$), the linearized measurement model is:
$$z = H x + e$$
Where $z \in \mathbb{R}^m$ is the measurement vector (voltage magnitudes, active/reactive branch flows), $x \in \mathbb{R}^n$ is the true grid state (voltage magnitudes and phase angles), $H \in \mathbb{R}^{m \times n}$ is the power-flow Jacobian matrix, and $e \sim \mathcal{N}(0, R)$ is Gaussian measurement noise.

Conventional Bad Data Detection (BDD) monitors the measurement residual:
$$r_z = z - H \hat{x}$$
$$\|r_z\|_2 = \|(I - H(H^T R^{-1} H)^{-1} H^T R^{-1}) z\|_2 \le \tau_{\text{BDD}}$$

### 1.2 The Stealthy FDI Cyber-Attack Subspace
An attacker with topology knowledge constructs an attack vector $a = H c$, where $c \in \mathbb{R}^n$ is an arbitrary state perturbation. The corrupted measurement becomes $z_a = z + a = z + H c$. The resulting residual is:
$$r_{z, a} = z_a - H \hat{x}_a = (z + H c) - H (\hat{x} + c) = z - H \hat{x} = r_z$$
Because $\|r_{z, a}\|_2 = \|r_z\|_2$, the attack completely bypasses traditional BDD alarms.

---

## 2. Mathematical Detection Framework

To defeat both instantaneous and stealthy drift attacks, our architecture implements two complementary statistical layers:

### 2.1 Layer 1: Spatial Mahalanobis Distance Engine
Under normal conditions, physical power flows follow correlated multivariate distributions: $x \sim \mathcal{N}(\mu, \Sigma)$. We define the normalized residual vector $r \in \mathbb{R}^N$:
$$r_i = \frac{x_i - \mu_i}{\sigma_i}$$
The squared Mahalanobis distance evaluates joint multivariate dispersion:
$$D^2 = r^T \Sigma^{-1} r = r^T W r$$
Where $W = \Sigma^{-1}$ is the inverse covariance (precision) matrix. Under $\mathcal{H}_0$, $D^2 \sim \chi_N^2$. The spatial decision rule is:
$$\text{Spatial\_Alert} = \begin{cases} 1, & \text{if } D^2 > T^2 \\ 0, & \text{otherwise} \end{cases}$$
Where $T^2 = \chi_N^2(1 - \alpha)$ is calibrated for a false alarm rate $\alpha \le 0.001$.

### 2.2 Layer 2: Temporal Two-Sided CUSUM Engine
Slow, stealthy bias injections ramp up gradually below $T^2$. The CUSUM filter accumulates sequential drift across time steps $n$:
$$S^+(n) = \max\left(0, \, S^+(n-1) + r_i(n) - \nu_0 - k\right)$$
$$S^-(n) = \max\left(0, \, S^-(n-1) - (r_i(n) - \nu_0 + k)\right)$$
Where:
- $\nu_0 = 0.0$ is the nominal mean of normalized residuals.
- $k$ is the reference allowance (slack parameter), set to $k \approx 1.0 \sigma_r$.
- $h$ is the decision threshold, set to $h \approx 4.0 \sigma_r$.

Temporal Decision Rule:
$$\text{Temporal\_Alert} = \begin{cases} 1, & \text{if } S^+(n) > h \text{ or } S^-(n) > h \\ 0, & \text{otherwise} \end{cases}$$

### 2.3 Aggregated Hardware Alarm
$$\text{FDI\_ALERT} = \text{Spatial\_Alert} \lor \text{Temporal\_Alert}$$

---

## 3. Fixed-Point Arithmetic & Precision Analysis

### 3.1 Signed Q1.15 Datapath Standard
The entire datapath is implemented in signed 16-bit **Q1.15** fixed-point representation:
- Total width: 16 bits.
- Format: 1 sign bit + 15 fractional bits.
- Range: $[-1.0, \, +0.999969482421875]$.
- LSB resolution: $\Delta = 2^{-15} \approx 3.0517578125 \times 10^{-5}$.

### 3.2 Multiplication & Saturation Mechanics
1. **Multiplication:** Multiplying two Q1.15 numbers yields a 32-bit signed product in **Q2.30** format (bits `[31:30]` are sign bits).
2. **Rounding:** Convergent half-up rounding offset $+2^{-16}$ (bit 14) is added to the 32-bit product before extracting bits `[30:15]`.
3. **Corner-Case Saturation:** The extreme product $(-1.0) \times (-1.0) = 0x8000 \times 0x8000 = 0x40000000$ represents $+1.0$, which cannot be represented in Q1.15. The multiplier detects this condition and saturates the output to `16'sh7FFF` ($+0.999969$), asserting an overflow flag.
4. **Intermediate Guard Bits:** The matrix-vector accumulator utilizes **34 bits** (2 guard bits for $N=4$ sums), guaranteeing mathematical immunity to intermediate overflow.

---

## 4. Hardware Architecture & RTL Implementation

```
+---------------------------------------------------------------------------------------------------------+
|                                    pmu_anomaly_top (Top-Level Entity)                                   |
|                                                                                                         |
|   +-----------------------+     +------------------------+     +------------------------------------+   |
|   | Input Handshake       |     | Preprocessor           |     | mahalanobis_matrix_engine          |   |
|   | data_valid/data_ready |==>  | r[i] = (x[i]-μ[i])*σ⁻¹ |==>  | Matrix Mult: y = W * r             |   |
|   | 4-Channel PMU Vector  |     | (Signed Q1.15)         |     | Dot Product: D² = rᵀ * y           |   |
|   +-----------------------+     +------------------------+     +-----------------+------------------+   |
|               ^                                                                  |                      |
|               | Control Strobes                                                  v D² (Q1.15)           |
|   +-----------+-----------+                                    +-----------------+------------------+   |
|   | pmu_fsm_ctrl          |                                    | cusum_filter_q15                   |   |
|   | Three-Process         |                                    | Two-sided S⁺, S⁻ accumulators      |   |
|   | Moore State Machine   |                                    | Zero-clamping max(0, .)            |   |
|   +-----------+-----------+                                    +-----------------+------------------+   |
|               |                                                                  |                      |
|               v Address / Write Strobes                                          v Updated State        |
|   +------------------------------------------------------------------------------+------------------+   |
|   | pmu_state_bram: On-Chip Synchronous Block RAM Storage (Channel S⁺, S⁻, Alert Counters)          |   |
|   +-------------------------------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------------------------------+
```

### 4.1 Three-Process Moore FSM Controller (`pmu_fsm_ctrl.sv`)
Strictly adheres to IEEE synchronous digital design standards:
- **Process 1 (`always_ff`):** Sequential state register with active-low asynchronous reset (`rst_n`).
- **Process 2 (`always_comb`):** Combinational next-state decoding based on `current_state`, `data_valid`, and completion handshakes.
- **Process 3 (`always_comb`):** Pure Moore combinational output logic. All output strobes (`latch_sample`, `preprocess_en`, `mahal_start`, `cusum_en`, `bram_we`) are functions solely of `current_state`.

FSM States:
`FSM_IDLE` $\to$ `FSM_CAPTURE` $\to$ `FSM_PREPROCESS` $\to$ `FSM_MAHALANOBIS` $\to$ `FSM_CUSUM` $\to$ `FSM_DECISION` $\to$ `FSM_STORE_RESULT` $\to$ `FSM_NEXT_CHANNEL` $\to$ `FSM_IDLE`.

### 4.2 On-Chip Block RAM State Storage (`pmu_state_bram.sv`)
Implements synchronous single-cycle memory using the Vivado synthesis directive `(* ram_style = "block" *)`. Preserves per-channel $S^+, S^-$ registers and alert counters across time-multiplexed sample evaluations.

---

## 5. Experimental Results & Verification

### 5.1 Dataset & Attack Scenarios
Simulated over 1,000 time steps using physical line parameters from the **IEEE 14-bus test feeder** (Line 1–2: $R = 0.01938$ p.u., $X = 0.05917$ p.u.):
- **Scenario 1 (Abrupt FDI, Samples 200–350):** Sudden false voltage injection on Bus 2 ($+0.035$ p.u.).
- **Scenario 2 (Gradual Drift, Samples 500–700):** Stealthy linear ramp on active power flow $P_{12}$ up to $+0.060$ p.u.
- **Scenario 3 (Coordinated Subspace, Samples 800–921):** Injection vector $a = H c$ matching the power-flow Jacobian.

### 5.2 Performance Comparison Table

| Metric | Proposed Dual-Layer (MD + CUSUM) | Baseline (Mahalanobis Alone) | Baseline (CUSUM Alone) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | **87.70%** | 86.20% | 87.30% |
| **Precision** | **97.03%** | 98.83% | 98.04% |
| **Recall** | **76.22%** | 71.55% | 74.52% |
| **F1-Score** | **0.8537** | 0.8300 | 0.8468 |
| **False Positive Rate** | **2.08%** | 0.76% | 1.32% |
| **Abrupt FDI Latency** | **0 samples (Instantaneous)** | 0 samples | 0 samples |
| **Gradual Drift Latency** | **76 samples** | 76 samples | 110 samples |
| **Stealthy Subspace Latency**| **0 samples (Instantaneous)** | 0 samples | 2 samples |

### 5.3 Discussion of Results
1. **Subspace Attack Resilience:** While coordinated attacks $a = H c$ evade static residual tests, cross-correlation tracking via the inverse covariance matrix $W$ instantly detects inter-bus correlation violations, triggering `spatial_alert_o` with 0 samples latency.
2. **Drift Detection:** In the gradual drift scenario, the bias is initially buried in Gaussian sensor noise. At sample 576, the cumulative positive sum $S^+$ breaches threshold $h$, raising a hardware interrupt before line thermal ratings are exceeded.

---

## 6. Vivado Handoff & Resource Utilization

Automated Tcl scripts are provided in `scripts/`:
- `scripts/create_project.tcl`: Configures target part (default: Artix-7 `xc7a35tcpg236-1`).
- `scripts/run_synthesis.tcl`: Performs elaboration and out-of-context synthesis.
- `scripts/run_implementation.tcl`: Executes place & route and static timing analysis.
- `scripts/run_simulation.tcl`: Executes behavioral simulation in XSim and exports waveforms.

### Estimated Resource Allocation:
- **DSP48 Slices:** 4–8 slices (matrix-vector multiplication and quadratic dot product).
- **Block RAM:** 1 RAMB18 primitive (or distributed LUTRAM depending on synthesis heuristics).
- **Slice LUTs / Registers:** $\approx 450 - 700$ LUTs, $350 - 550$ FFs.
- **Estimated $F_{\max}$:** $> 150\text{ MHz}$ on Artix-7 speed grade -1.

---

## 7. Conclusion & Future Scalability

This project successfully proves the feasibility and high performance of hardware-accelerated statistical anomaly detection for smart grids. The modular architecture easily scales to larger power grids (e.g., IEEE 30-bus, IEEE 118-bus) by expanding the dimension parameter `N_DIM` and precision matrix memory depth without altering the core Three-Process Moore FSM or CUSUM filter topology.

