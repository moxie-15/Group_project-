# Hardware Architecture Specification
## Smart Grid False Data Injection (FDI) Anomaly Detection Engine via Mahalanobis Distance & CUSUM

**Document Version:** 1.0.0  
**Design Phase:** Stage 1 — System Specification and Architectural Design  
**Target Hardware:** AMD / Xilinx 7-Series (Artix-7 / Zynq-7000) & UltraScale+  
**Implementation Standard:** Synthesizable SystemVerilog (IEEE 1800-2017)  

---

## 1. System Overview & Objective

The **FDI Anomaly Detection Engine** provides real-time, microsecond-latency hardware protection for smart grid state estimators against stealthy False Data Injection (FDI) cyber-attacks. 

Traditional Bad Data Detection (BDD) algorithms in power grids rely on static $L_2$-norm measurement residual tests:
$$J(x) = \| z - H\hat{x} \|_2 \le \tau$$
Stealthy cyber-attackers inject structured perturbation vectors $a = H c$ into sensor measurements $z_{\text{attack}} = z + a$, leaving the state estimation residual unchanged:
$$\| z + a - H(\hat{x} + c) \|_2 = \| z - H\hat{x} \|_2$$

To defeat this vulnerability, our hardware engine implements a **dual-layer detection topology**:
1. **Spatial Anomaly Detection (Mahalanobis Distance Engine):** Evaluates joint correlation across physical sensor measurements against an empirical inverse covariance (precision) matrix $W = \Sigma^{-1}$. Even if individual sensor values appear plausible, uncoordinated manipulations violate power-flow spatial correlations.
2. **Temporal Anomaly Detection (Two-Sided CUSUM Engine):** Accumulates sequential small deviations over time to detect slow-onset, low-magnitude persistent bias injections that intentionally fly beneath the instantaneous spatial threshold $T^2$.

```
+---------------------------------------------------------------------------------------------------------+
|                                        FDI ANOMALY ENGINE TOP-LEVEL                                     |
|                                                                                                         |
|   +-----------------------+     +------------------------+     +------------------------------------+   |
|   | Measurement Inputs    |     | Preprocessor           |     | Mahalanobis Distance Engine        |   |
|   | (Raw PMU Telemetry)   |     |                        |     |                                    |   |
|   | x0, x1, x2, x3        |==>  | Normalized Residual:   |==>  | Matrix-Vector Mult: y = W * r      |   |
|   | Handshake: Valid/Ready|     | r[i] = (x[i]-μ[i])/σ[i]|     | Quadratic Dot:   D_M² = rᵀ * y     |   |
|   +-----------------------+     +------------------------+     +-----------------+------------------+   |
|                                                                                  |                      |
|                                                                                  | D_M² (Q16.16)        |
|                                                                                  v                      |
|   +-----------------------+     +------------------------+     +-----------------+------------------+   |
|   | Combined Alerts       |     | Decision Logic         |     | CUSUM Detection Engine             |   |
|   | - FDI_ALERT           |<==  | - Spatial: D_M² > T²   |<==  | - Positive Sum: S⁺(n)              |   |
|   | - MAHALANOBIS_ALERT   |     | - Temporal: S⁺ > h     |     | - Negative Sum: S⁻(n)              |   |
|   | - CUSUM_POS_ALERT     |     |             S⁻ > h     |     | Recursive update with zero clamp   |   |
|   | - CUSUM_NEG_ALERT     |     +------------------------+     +------------------------------------+   |
|   +-----------------------+                 ^                                                           |
|                                             | Config Bus (T², h, k, ν₀, W, μ, σ)                        |
|                                 +-----------+------------+                                              |
|                                 | Configuration Registers|                                              |
|                                 +------------------------+                                              |
+---------------------------------------------------------------------------------------------------------+
```

---

## 2. Initial Four-Dimensional Measurement Definition

For the initial prototype, we formulate a 4-dimensional telemetry vector ($N = 4$):
$$x[n] = \begin{bmatrix} x_0[n] \\ x_1[n] \\ x_2[n] \\ x_3[n] \end{bmatrix} = \begin{bmatrix} V_1[n] \\ V_2[n] \\ P_{12}[n] \\ Q_{12}[n] \end{bmatrix}$$

- $x_0 = V_1$: Voltage magnitude at Bus 1 (Nominal $\sim 1.00$ p.u.)
- $x_1 = V_2$: Voltage magnitude at Bus 2 (Nominal $\sim 0.98$ p.u.)
- $x_2 = P_{12}$: Active power flow from Bus 1 to Bus 2 (Nominal $\sim 0.45$ p.u.)
- $x_3 = Q_{12}$: Reactive power flow from Bus 1 to Bus 2 (Nominal $\sim 0.12$ p.u.)

All baseline statistics ($\mu$, $\sigma$, and $\Sigma^{-1}$) are derived via rigorous offline power system calibration using Newton-Raphson load-flow simulations with physical Gaussian measurement noise.

---

## 3. Signal Flow & Pipeline Architecture

The hardware pipeline operates across five sequential stages:

```
Cycle 0: Ingestion & Handshake Latch
         ├── Input: x[0..3] (Raw Telemetry)
         └── Handshake: data_valid && data_ready asserted

Cycle 1: Preprocessing & Normalization
         └── r[i] = (x[i] - mu[i]) * inv_sigma[i]   (Q4.12 Signed)

Cycle 2..5: Folded Matrix-Vector Multiplier (y = W * r)
         ├── Cycle 2: Row 0 dot product  -> y[0]   (Q12.22 Signed)
         ├── Cycle 3: Row 1 dot product  -> y[1]   (Q12.22 Signed)
         ├── Cycle 4: Row 2 dot product  -> y[2]   (Q12.22 Signed)
         └── Cycle 5: Row 3 dot product  -> y[3]   (Q12.22 Signed)

Cycle 6..7: Quadratic Dot-Product Unit (D_M² = rᵀ * y)
         ├── Cycle 6: Parallel Multipliers: p[i] = r[i] * y[i]  (Q16.34 Signed)
         └── Cycle 7: Summation Tree & Format Conversion -> D_M² (Q16.16 Signed)

Cycle 8: Dual-Layer Decision & CUSUM Evaluation
         ├── Spatial Check:  D_M² > T²
         ├── Temporal Check: S⁺(n) = max(0, S⁺(n-1) + D_M² - ν₀ - k)
         │                   S⁻(n) = max(0, S⁻(n-1) - D_M² + ν₀ - k)
         └── Decision Logic: FDI_ALERT = Spatial_Alert | Cusum_Pos_Alert | Cusum_Neg_Alert
```

### Total Latency Budget
- **Latency:** Exactly **9 clock cycles** from `data_valid` assertion to registered output alert.
- **Throughput:** In folded mode, a new sample can be ingested every **4 clock cycles**.
- At a conservative $100\text{ MHz}$ system clock ($T_{\text{clk}} = 10\text{ ns}$):
  - **Total Latency:** $9 \times 10\text{ ns} = \mathbf{90\text{ ns}}$.
  - **Maximum Processing Rate:** $25\text{ Million vectors/second}$.
  - Compared to standard PMU reporting rates ($30 - 60\text{ frames/second}$), the FPGA engine delivers an acceleration factor $> 400,000\times$, completely eliminating computational bottlenecks.

---

## 4. Proposed RTL Module Hierarchy

Following strict modular digital design standards:

```
smart_grid_fdi_fpga/rtl/
├── fdi_pkg.sv                   // Package: Fixed-point bit widths, structs, saturation functions
├── fdi_top.sv                   // Top-Level wrapper connecting all submodules and control ports
├── measurement_preprocessor.sv  // Mean centering and variance scaling: r[i] = (x[i] - μ[i]) / σ[i]
├── mahalanobis_engine.sv        // Coordinate wrapper for MVM and dot-product
│   ├── matrix_vector_multiplier.sv  // Computes y = W * r using inferred DSP multipliers
│   ├── fixed_point_multiplier.sv    // Parameterized signed fixed-point multiplier slice
│   ├── fixed_point_accumulator.sv   // Parameterized accumulator with guard bits
│   └── quadratic_dot_product.sv     // Computes D_M² = rᵀ * y
├── cusum_detector.sv            // Two-sided recursive CUSUM engine (S⁺, S⁻) with zero clamping
├── fdi_decision_logic.sv        // Real-time alarm aggregation and sticky interrupt registers
└── config_registers.sv          // Memory-mapped configuration storage (T², h, k, ν₀, W, μ)
```

---

## 5. Configuration & Calibration Strategy

1. **Offline Training (Python):**
   - Ingests $M = 10,000$ baseline time steps of normal grid operation.
   - Calculates empirical mean $\hat{\mu} = \frac{1}{M}\sum x[n]$.
   - Calculates empirical covariance $\hat{\Sigma} = \frac{1}{M-1}\sum (x[n]-\hat{\mu})(x[n]-\hat{\mu})^T$.
   - Computes precision matrix $W = \hat{\Sigma}^{-1}$ using Cholesky or SVD regularization to ensure positive definiteness.
   - Computes theoretical reference values: $\nu_0 = N = 4.0$.
   - Calibrates empirical thresholds: $T^2 = \chi_4^2(1 - \alpha)$, $k = \frac{\delta}{2}$, and $h$ chosen to bound Average Run Length (ARL) under normal conditions.
2. **Fixed-Point Quantization & Export:**
   - Converts floating-point parameters to designated signed fixed-point hex integers.
   - Exports coefficients directly to `data/reference/calibration_coefficients.csv`.
3. **Hardware Loading:**
   - RTL registers default to pre-calibrated baseline parameters on reset.
   - Dynamic reconfiguration supported through the configuration register port.

