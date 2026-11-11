# Oral Exam & Project Defense Preparation (Q&A)
## Group 9: Smart Grid False Data Injection (FDI) Anomaly Engine

Use this document to prepare for questions from your lecturer, teaching assistants, or exam committee during your project defense and live demonstration.

---

### Question 1: Why did you choose signed Q1.15 fixed-point arithmetic instead of IEEE-754 32-bit floating-point?
**Model Answer:**  
*"In FPGA hardware design, 32-bit floating-point arithmetic units (like FP multipliers and FP adders) introduce multi-cycle latencies (typically 3 to 7 clock cycles per operation), consume hundreds of Slice LUTs, and require heavy clock routing.  
In contrast, signed 16-bit Q1.15 fixed-point arithmetic maps directly into the native hardware architecture of AMD/Xilinx DSP48 slices (which feature an $18 \times 25$-bit signed multiplier). A Q1.15 multiply-accumulate operation finishes in a single clock cycle with zero logic slice overhead, enabling our engine to achieve a 90 ns total detection latency at 100 MHz. Furthermore, with an LSB resolution of $2^{-15} \approx 3.05 \times 10^{-5}$ p.u., Q1.15 provides more than enough precision to resolve subtle smart grid PMU voltage fluctuations, which typically have a noise floor around $10^{-3}$ p.u."*

---

### Question 2: How do you handle the corner-case multiplication of $-1.0 \times -1.0$ in Q1.15, and why does it matter?
**Model Answer:**  
*"In two's complement Q1.15 representation, the valid range is strictly $[-1.0, \, +0.999969]$ (`0x8000` to `0x7FFF`). The value $+1.0$ cannot be represented.  
When multiplying $-1.0 \times -1.0$ (`0x8000` $\times$ `0x8000`), the raw 32-bit product is `0x4000_0000`. If naive bit-slicing is used (`[30:15]`), this wraps around to `0x8000` (which is $-1.0$), resulting in catastrophic positive-to-negative sign inversion.  
In our `fixed_point_multiplier.sv` module and `fdi_pkg::q15_mult` function, we explicitly detect when both inputs are `16'sh8000`. When detected, we clamp the output to maximum positive saturation `16'sh7FFF` (`+0.999969`) and assert an overflow flag. This ensures our datapath is 100% mathematically stable."*

---

### Question 3: Why is a Three-Process Moore FSM required, and how does it prevent glitches compared to Mealy or single-process FSMs?
**Model Answer:**  
*"The canonical Three-Process Moore FSM separates state logic into three distinct SystemVerilog blocks:
1. An `always_ff` synchronous sequential block for the state register and asynchronous active-low reset.
2. An `always_comb` block for combinational next-state transitions.
3. An `always_comb` block for pure Moore output logic.
In a Mealy machine, outputs depend on both the current state and asynchronous input signals, making output strobes vulnerable to combinational input glitches and race conditions. In our Moore FSM, output strobes (like `bram_we`, `mahal_start`, and `cusum_en`) are strictly decoupled from input transitions—they depend exclusively on the registered `current_state`. This eliminates glitching on critical write-enable lines and guarantees predictable multi-cycle execution across all PMU channels."*

---

### Question 4: Why do we need a Dual-Layer Detection architecture? Why isn't Mahalanobis distance alone sufficient?
**Model Answer:**  
*"Because cyber-attackers use different attack vectors:
1. **Spatial Mahalanobis Distance ($D^2 = r^T \Sigma^{-1} r$)** is exceptional at catching cross-channel correlation violations and abrupt attacks instantly (in 0 clock cycles). However, an intelligent adversary can design a **gradual drift attack** (a very slow linear ramp) where the deviation at any single instant is smaller than the spatial threshold $T^2$.
2. **Temporal CUSUM ($S^+ = \max(0, S^+ + e - k)$)** recursively accumulates sequential positive deviations over time. Even if the instantaneous bias is small, the persistent positive shift drives $S^+$ steadily upward until it breaches decision threshold $h$.
In our experimental evaluation on IEEE 14-bus telemetry, the Mahalanobis detector caught abrupt attacks instantly, while CUSUM caught the gradual drift at sample 576. Combining them provides 87.7% accuracy and 97.03% precision."*

---

### Question 5: How does an attacker construct a stealthy attack vector $a = H c$, and why does your design catch it?
**Model Answer:**  
*"In traditional power system state estimation, the linearized measurement model is $z = H x + e$. Bad Data Detection checks the residual $r_z = z - H\hat{x}$.  
If an attacker injects $a = H c$, where $c$ is an arbitrary voltage/angle shift, the new residual is:
$$\|z_a - H\hat{x}_a\| = \|(z + Hc) - H(\hat{x} + c)\| = \|z - H\hat{x}\|$$
The residual remains completely unchanged, so standard static software BDD is mathematically blind to the attack.  
Our FPGA design catches it through the **inverse covariance precision matrix $W = \Sigma^{-1}$**. While $a = Hc$ satisfies the DC approximation of power flow, real transmission lines have reactive power coupling and correlated thermal losses. The physical covariance matrix $\Sigma$ captures the true joint variance of physical bus voltages and line flows. When the attacker manipulates multiple buses, the quadratic form $D^2 = r^T \Sigma^{-1} r$ triggers a spatial alert immediately because the attack violates empirical physical sensor cross-correlations."*

---

### Question 6: How did you ensure that Xilinx Vivado infers dedicated Block RAM (BRAM) rather than distributed slice LUTRAM?
**Model Answer:**  
*"In [`rtl/pmu_state_bram.sv`](file:///c:/Users/MOXIE/Desktop/group_project/rtl/pmu_state_bram.sv), we applied two critical techniques:
1. **Synthesis Attribute:** We declared the memory array with `(* ram_style = "block" *) logic [STATE_WIDTH-1:0] ram_block [DEPTH];`, which instructs Vivado synthesis heuristics to map the array to dedicated Block RAM primitives (`RAMB18E1` or `RAMB36E1`).
2. **Synchronous Clocked Read:** In Xilinx FPGAs, distributed LUTRAM allows asynchronous combinational reads (`assign dout = ram[addr]`), whereas physical Block RAM primitives require synchronous clocked read registers (`always_ff @(posedge clk) dout <= ram[addr]`). We structured the read and write operations inside an `always_ff` synchronous block, matching the hardware architecture of dedicated BRAM tiles."*

---

### Question 7: What is the hardware latency and maximum stream throughput of your FPGA engine?
**Model Answer:**  
*"The complete datapath from input handshake (`data_valid`) to registered interrupt output (`fdi_alert_o`) takes **9 clock cycles**:
- 1 cycle for input latching and normalization.
- 4 cycles for folded matrix-vector multiplication.
- 2 cycles for quadratic dot-product accumulation.
- 2 cycles for CUSUM filtering, threshold comparison, and BRAM write-back.
At a conservative **100 MHz clock** ($T_{\text{clk}} = 10\text{ ns}$), total latency is **$90\text{ nanoseconds}$**.  
Because the pipeline can ingest a new 4-channel measurement frame every 4 clock cycles, the continuous stream throughput is:
$$\text{Throughput} = \frac{100\text{ MHz}}{4\text{ cycles/sample}} = \mathbf{25\text{ Million samples/second}}$$
Since standard smart grid PMUs report at $30 - 60\text{ frames/second}$, our FPGA engine delivers an acceleration factor greater than $400,000\times$, allowing a single low-cost FPGA to monitor hundreds of smart grid substations concurrently."*

---

### Question 8: How did you calibrate the spatial threshold $T^2$ and CUSUM drift parameters $k$ and $h$?
**Model Answer:**  
*"We followed empirical statistical calibration using clean baseline data (the first 200 normal samples):
1. **Spatial Threshold $T^2$:** Under $\mathcal{H}_0$, $D^2$ follows a Chi-square distribution with 4 degrees of freedom ($\chi_4^2$). Using the clean training set, we evaluated $D^2$ and set $T^2 = 2600$ LSBs (`0x0A28` in Q1.15), which matches the 99.5th percentile bound to enforce a False Positive Rate $< 1\%$.
2. **CUSUM Slack Parameter $k$:** In statistical quality control (Siegmund's continuous approximation), optimal drift allowance is set to $k = \frac{\delta_{\min}}{2} \approx 1.0 \sigma_r$. For our normalized residuals ($\sigma_r \approx 5100$ LSBs), we set $k = 6500$ LSBs (`0x1964` in Q1.15).
3. **CUSUM Decision Threshold $h$:** Chosen to balance Average Run Length under normal conditions ($ARL_0 > 500$ frames) and detection speed. We set $h = 22000$ LSBs (`0x55F0` in Q1.15), which prevents random sensor noise excursions from triggering false alarms while detecting power ramps within 76 samples."*

---

### Question 9: How did you verify bit-accuracy between your SystemVerilog RTL and your Python reference model?
**Model Answer:**  
*"We built an exact bit-accurate software model in [`python/golden_model.py`](file:///c:/Users/MOXIE/Desktop/group_project/python/golden_model.py) that mirrors every arithmetic operation in `fdi_pkg.sv`:
- It emulates two's complement 16-bit integer math using `np.int16`.
- It replicates full 32-bit multiplication followed by half-up rounding (`+ 0x4000`) and arithmetic shift (`>> 15`).
- It implements the identical corner-case saturation for $-1.0 \times -1.0$.
- It emulates BRAM channel state storage across time steps.
The CSV testbench [`testbench/tb_pmu_anomaly_top.sv`](file:///c:/Users/MOXIE/Desktop/group_project/testbench/tb_pmu_anomaly_top.sv) reads the exact same telemetry and logs the hardware output. Our verification script [`python/verify_rtl_output.py`](file:///c:/Users/MOXIE/Desktop/group_project/python/verify_rtl_output.py) confirms that hardware RTL results match Python golden results with a maximum error delta of $\le 1$ LSB (attributable solely to fixed-point rounding boundary conditions)."*

---

### Question 10: How can this design scale from the initial 4-channel feeder prototype to full IEEE 14-bus, 30-bus, or 118-bus power grids?
**Model Answer:**  
*"Our SystemVerilog implementation is fully parameterized:
- Channel dimension is parameterized via `parameter int N = N_CHANNELS` in `fdi_pkg.sv`.
- To scale to an IEEE 14-bus system (14 bus voltages + 20 branch flows = 34 measurements), we simply set `N = 34` and adjust the BRAM address width `CHANNEL_BITS = 6` ($2^6 = 64$ entries).
- The Three-Process Moore FSM controller automatically iterates through all $N$ channels before asserting `frame_done_o`.
- Because modern mid-range FPGAs (like the AMD/Xilinx Artix-7 or Zynq-7000) have up to 220 DSP48 slices and several megabits of Block RAM, scaling to IEEE 30-bus requires less than 20% of chip capacity while maintaining full wire-speed operation."*

