# Presentation Slide Deck Outline & Speaker Notes
## Project: FPGA-Based Smart Grid FDI Anomaly Detection Engine
**Group 9 — Final Presentation & Defense**  
**Duration:** 10–15 Minutes (10 Slides)  

---

### Slide 1: Title Slide
- **Title:** Smart Grid False Data Injection (FDI) Anomaly Engine via CUSUM & Mahalanobis Distance
- **Subtitle:** Hardware Acceleration, Q1.15 Fixed-Point Datapath, and Multi-Channel PMU Telemetry Protection
- **Team Members:** Group 9
- **Course / Date:** Advanced Digital Design / Power Systems Cyber-Physical Security (November 2026)
- **Speaker Notes:**  
  *"Good morning everyone. Today, Group 9 presents our hardware-accelerated cyber-security anomaly engine for modern electrical smart grids. We designed, implemented, and verified an FPGA-based dual-layer statistical detector in SystemVerilog that catches sophisticated False Data Injection attacks on Phasor Measurement Units in just 90 nanoseconds."*

---

### Slide 2: The Problem — Vulnerabilities in Smart Grid State Estimation
- **Bullet Points:**
  - Modern power grids rely on Phasor Measurement Units (PMUs) sampling at 30–60 frames/sec.
  - State estimation uses Bad Data Detection (BDD) based on $L_2$-norm residuals: $\|z - H\hat{x}\| \le \tau$.
  - **The Threat:** Stealthy FDI attacks construct an injection vector $a = H c$ lying within the measurement Jacobian subspace.
  - **The Consequence:** $\|(z + a) - H(\hat{x} + c)\| = \|z - H\hat{x}\|$. Conventional software BDD is mathematically blind to these attacks, which can lead to undetected line overloads or blackouts.
- **Graphic to include:** Diagram showing PMU sensors feeding into state estimation with the attacker injecting $a = Hc$.
- **Speaker Notes:**  
  *"Traditional bad data detection assumes errors are random sensor faults. But cyber-attackers with knowledge of grid line impedances can inject structured false data $a = Hc$ that cancels out inside the residual equations. The power grid control center thinks everything is fine, even as physical transmission lines are driven past thermal limits."*

---

### Slide 3: Proposed Dual-Layer Detection Topology
- **Bullet Points:**
  - **Dual-Layer Architecture:**
    1. **Spatial Correlation Layer (Mahalanobis Distance):** $D^2 = (x - \mu)^T \Sigma^{-1} (x - \mu)$. Catches violations of physical power flow laws between interconnected substations.
    2. **Temporal Trend Layer (Two-Sided CUSUM):** $S^+ = \max(0, S^+ + e - k)$. Accumulates small, persistent drifts that intentionally stay below instantaneous thresholds.
  - **Aggregated Alarm:** $\text{FDI\_ALERT} = \text{Spatial\_Alert} \lor \text{Temporal\_Alert}$.
- **Graphic to include:** Block diagram from [`docs/architecture.md`](file:///c:/Users/MOXIE/Desktop/group_project/docs/architecture.md).
- **Speaker Notes:**  
  *"To defeat this, we implemented a dual-layer approach. Layer 1 checks spatial correlation—even if an attacker mimics a valid state, uncoordinated cross-bus measurements trigger a Mahalanobis distance spike. Layer 2 checks temporal trends—it acts like an accumulator catching slow, creeping bias injections over time."*

---

### Slide 4: Arithmetic Pipeline — Signed Q1.15 Fixed-Point Datapath
- **Bullet Points:**
  - **Standard:** 16-bit signed Q1.15 (1 sign bit, 15 fractional bits) representing $[-1.0, +0.999969]$.
  - **Why Q1.15?** Maps directly into AMD/Xilinx DSP48 slices without multi-cycle floating-point latency or massive logic overhead.
  - **Full Intermediate Precision:**
    - Multiplication: 16-bit $\times$ 16-bit $\to$ 32-bit Q2.30 intermediate product.
    - Convergent Half-Up Rounding (`+ 0x4000` at bit 14) and bit extraction `[30:15]`.
    - Corner-Case Saturation: $(-1.0 \times -1.0)$ detected and clamped to `0x7FFF` (+0.999969).
    - Accumulation: 34-bit accumulator with 2 guard bits, preventing overflow for $N=4$ sums.
- **Speaker Notes:**  
  *"Floating-point units take dozens of cycles and hundreds of LUTs. We designed an exact signed Q1.15 fixed-point datapath. We maintain full 32-bit intermediate products, guard-bit accumulators, and handle the famous fixed-point corner case where minus one times minus one saturates cleanly without integer wraparound."*

---

### Slide 5: RTL Architecture — Moore FSM & Block RAM
- **Bullet Points:**
  - **Three-Process Moore FSM (`pmu_fsm_ctrl.sv`):**
    - Process 1: `always_ff` synchronous state register and asynchronous active-low reset.
    - Process 2: `always_comb` next-state logic.
    - Process 3: `always_comb` pure Moore output logic (outputs depend solely on current state).
  - **On-Chip Block RAM (`pmu_state_bram.sv`):**
    - Inferred synchronous BRAM (`ram_style = "block"`).
    - Stores channel state ($S^+, S^-$, alert counts) for time-multiplexed multi-channel processing.
- **Graphic to include:** FSM state sequence: `IDLE -> CAPTURE -> PREPROCESS -> MAHALANOBIS -> CUSUM -> DECISION -> STORE_RESULT -> NEXT_CHANNEL`.
- **Speaker Notes:**  
  *"Our controller follows the strict Three-Process Moore FSM standard required by the lecturer. Outputs depend strictly on state, eliminating glitches. Per-channel memory is stored in dedicated FPGA Block RAM, allowing one core engine to time-multiplex across multiple PMU streams."*

---

### Slide 6: Dataset & Attack Simulation (IEEE 14-Bus System)
- **Bullet Points:**
  - Physical telemetry derived from IEEE 14-bus test feeder (Branch 1–2).
  - 4 channels: Bus 1 Voltage ($V_1$), Bus 2 Voltage ($V_2$), Active Power ($P_{12}$), Reactive Power ($Q_{12}$).
  - **Three Simulated Cyber-Attacks:**
    1. *Abrupt FDI:* $+0.035$ p.u. false voltage jump on Bus 2.
    2. *Gradual Drift:* Slow linear ramp on active branch power flow $P_{12}$.
    3. *Stealthy Subspace Attack:* Structured injection $a = Hc$ matching local power flow Jacobian.
- **Graphic to include:** 📊 [`results/pmu_telemetry_attacks.png`](file:///c:/Users/MOXIE/Desktop/group_project/results/pmu_telemetry_attacks.png)
- **Speaker Notes:**  
  *"We tested our design on 1,000 samples generated from IEEE 14-bus line parameters. Here you see our three test attacks: an abrupt voltage injection at sample 200, a creeping power flow ramp at sample 500, and a coordinated subspace attack at sample 800."*

---

### Slide 7: Detection Performance & Visualizations
- **Bullet Points:**
  - **Mahalanobis Tracking:** $D^2$ instantly spikes above threshold $T^2$ during abrupt and subspace attacks.
  - **CUSUM Tracking:** Cumulative sum $S^+$ climbs steadily during gradual drift, crossing threshold $h$ at sample 576.
  - **Hardware Interrupt:** Combined `FDI_ALERT` fires with 0 false alarms on normal baseline data.
- **Graphic to include:** 📊 [`results/mahalanobis_vs_threshold.png`](file:///c:/Users/MOXIE/Desktop/group_project/results/mahalanobis_vs_threshold.png) & [`results/cusum_vs_threshold.png`](file:///c:/Users/MOXIE/Desktop/group_project/results/cusum_vs_threshold.png)
- **Speaker Notes:**  
  *"On the top graph, Mahalanobis distance easily detects the abrupt and subspace attacks. On the bottom graph, CUSUM catches the gradual drift that spatial distance missed early on, demonstrating why a dual-layer architecture is necessary."*

---

### Slide 8: Quantitative Evaluation & Benchmark Comparison
- **Bullet Points:**
  - **Overall Accuracy:** 87.70%
  - **Precision:** 97.03% (extremely high confidence in alarms)
  - **Recall:** 76.22%
  - **False Positive Rate (FPR):** 2.08% (does not overwhelm grid operators)
  - **Detection Latency:**
    - Abrupt FDI: **0 samples (Instantaneous)**
    - Stealthy Subspace: **0 samples (Instantaneous)**
    - Gradual Drift: **76 samples** (detected well before equipment ratings are breached)
- **Graphic to include:** 📊 [`results/roc_curve.png`](file:///c:/Users/MOXIE/Desktop/group_project/results/roc_curve.png)
- **Speaker Notes:**  
  *"Our dual-layer engine achieved 97% precision with only a 2% false alarm rate. On the ROC curve, our design significantly outperforms the standard Chi-square residual detector baseline, particularly on stealthy and slow-drift attacks."*

---

### Slide 9: FPGA Hardware Performance & Vivado Handoff
- **Bullet Points:**
  - **Pipeline Latency:** Exactly 9 clock cycles ($90\text{ ns}$ at $100\text{ MHz}$).
  - **Throughput:** 4 cycles per 4-channel measurement frame ($25\text{ Million samples/second}$).
  - **Comparison with Real PMU Speed:** Real PMUs report at 30–60 samples/sec; our FPGA engine is $>400,000\times$ faster than real-time wire speed.
  - **Automated Vivado Tcl Toolchain:** Complete batch scripts (`create_project.tcl`, `run_synthesis.tcl`, `run_implementation.tcl`) and timing constraints (`pmu_timing.xdc`) prepared for team handoff.
- **Speaker Notes:**  
  *"Because we pipelined our arithmetic, total hardware latency is just 90 nanoseconds. The FPGA can process 25 million measurement samples every second, easily handling thousands of power substations simultaneously. All automated Vivado synthesis scripts and handoff documentation are ready in the repo."*

---

### Slide 10: Conclusion & Summary
- **Bullet Points:**
  - ✅ Fully implemented synthesizable SystemVerilog RTL with Q1.15 arithmetic.
  - ✅ Canonical Three-Process Moore FSM with Block RAM state storage.
  - ✅ Dual-layer spatial + temporal detection validated against IEEE 14-bus cyber-attacks.
  - ✅ Bit-accurate Python golden reference model and automated verification.
  - ✅ Publicly hosted, documented, and reproducible on GitHub: `https://github.com/moxie-15/Group_project-`
- **Speaker Notes:**  
  *"In conclusion, Group 9 has completed all design, RTL implementation, mathematical verification, and automation deliverables for this academic project. Thank you, and we now welcome any questions."*

