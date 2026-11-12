# -*- coding: utf-8 -*-
"""
Chapter 4 generator for CPE 503 Group 09 report.
Details the 10-step design flow, SystemVerilog RTL architecture, schematics,
Table 4.1 (FSM States and Operational Sequence - Lecturer Table 3),
and Table 4.2 (Hardware Timing and Complexity Analysis - Lecturer Table 7).
"""

def get_chapter_four():
    return r"""
% =====================================================================
% CHAPTER FOUR
% =====================================================================
\chapter{Methodology and Hardware Implementation}

\section{Overall Methodology and Repeatable 10-Step Design Flow}
To ensure technical rigor, repeatability, and complete traceability between high-level
mathematics and physical digital hardware, the engineering methodology follows a structured
10-step design flow:
\begin{enumerate}
    \item \textbf{Step 1: System Specification:} Define functional requirements, input telemetry
    formats (signed Q1.15), target reporting rates ($F_s = 50~\text{Hz}$ under IEEE~C37.118),
    and threat models (stealth, ramp, scaling, and replay FDI).
    \item \textbf{Step 2: Floating-Point Algorithmic Model:} Implement a software prototype in
    Python to formulate the mathematical state estimator, Mahalanobis distance, and two-sided
    CUSUM algorithms.
    \item \textbf{Step 3: Bit-Accurate Fixed-Point Golden Model:} Translate the floating-point
    model into an exact, integer-scaled Q1.15 bit-accurate golden model in Python. Every hardware
    output is verified against this reference.
    \item \textbf{Step 4: Microarchitecture Design:} Develop block diagrams, state transition
    graphs, memory maps, and datapath schedules. Choose between parallel and time-multiplexed
    hardware topologies.
    \item \textbf{Step 5: Synthesizable RTL Description:} Code the design in SystemVerilog
    (IEEE 1800-2017) using fully parameterizable word lengths and strictly synthesizable constructs.
    \item \textbf{Step 6: Functional \& Assertion-Based Verification:} Construct self-checking
    SystemVerilog testbenches with known-answer test (KAT) vectors and automated mismatch detection.
    \item \textbf{Step 7: Logic Synthesis and Technology Mapping:} Synthesize the RTL in AMD/Xilinx
    Vivado in accordance with Vivado synthesis and constraint guidelines \cite{ug901,ug903,ug907} targeting the Artix-7 XC7A200T FPGA; extract resource utilization (LUTs, FFs, DSPs, BRAM).
    \item \textbf{Step 8: Timing and Power Analysis:} Evaluate static timing slack (WNS/WHS),
    maximum clock frequency ($f_{\max}$), and dynamic power consumption via Vivado report tools.
    \item \textbf{Step 9: Automated Telemetry \& CSV Data Export:} Execute automated regression
    scripts that write hardware outputs to CSV format for statistical performance analysis.
    \item \textbf{Step 10: Reproducibility Package Assembly:} Archive all RTL, testbenches, Python
    scripts, synthesis Tcl files, and raw simulation datasets into an open, documented repository.
\end{enumerate}

\section{Python Telemetry Generation and IEEE 14-Bus Test System}
To evaluate the anomaly engine under realistic power grid operating conditions, telemetry
streams are derived from the standard IEEE 14-bus transmission network benchmark \cite{matpowercase14}.
The IEEE 14-bus system represents a portion of the Midwestern American electric power system,
comprising 5 synchronous generators, 14 transmission buses, and 20 interconnecting lines.

The Python data generator executes a steady-state Newton-Raphson power-flow solution using
MATPOWER reference formulations \cite{zimmerman2011,matpowercase14}. A four-dimensional synchrophasor measurement configuration
is extracted:
\begin{equation}
\boldsymbol{z}_t = [V_{1,t}, \; V_{2,t}, \; P_{12,t}, \; Q_{12,t}]^T,
\end{equation}
where $V_1, V_2$ represent voltage magnitudes at Bus 1 (slack bus) and Bus 2 (generator bus),
and $P_{12}, Q_{12}$ denote the active and reactive power flows traversing the high-voltage
transmission branch connecting Bus 1 and Bus 2. Stationary Gaussian measurement noise is
superimposed onto all channels ($\sigma = 0.005\text{--}0.020~\text{p.u.}$) to emulate physical
instrument transformer and PMU analog-to-digital conversion noise.

\section{Cyber-Attack Injection Simulation}
Across the 1,200 continuous frames generated at $F_s = 50~\text{Hz}$ ($20~\text{ms}$ interval,
$24.0~\text{s}$ total sequence), four distinct cyber-attack modalities are injected:
\begin{itemize}
    \item \textbf{Scenario 1: Coordinated Stealth FDI ($t = 200\text{--}349$, 150 frames):}
    The adversary computes the measurement Jacobian $\boldsymbol{H}$ and injects a covert
    perturbation $\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$, where $\boldsymbol{c}$ applies
    a false $+0.035~\text{rad}$ phase angle bias. Active power flow $P_{12}$ shifts by $+0.045~\text{p.u.}$
    while $V_2$ shifts by $-0.015~\text{p.u.}$, perfectly evading classical $\chi^2$ bad data detection.
    \item \textbf{Scenario 2: Gradual Ramp / Drift Attack ($t = 450\text{--}649$, 200 frames):}
    A subtle linear ramp is introduced at a rate of $+0.0004~\text{p.u./frame}$ ($+0.08~\text{p.u.}$ total).
    The gradual slope bypasses instantaneous threshold checkers, testing the CUSUM integration capability.
    \item \textbf{Scenario 3: Multi-Channel False Scaling Attack ($t = 750\text{--}869$, 120 frames):}
    Telemetry is scaled by a multiplicative factor of $+5.0\%$ ($(1 + \alpha)\boldsymbol{z}_t$, $\alpha = 0.05$),
    amplifying both steady-state loading and high-frequency noise.
    \item \textbf{Scenario 4: Historical Replay Attack ($t = 950\text{--}1070$, 121 frames):}
    Telemetry recorded during clean historical frames ($t = 50\text{--}170$) is replayed during an
    actual physical grid load excursion, masking the true operational state from operators.
\end{itemize}

\section{Calibration and Evaluation Dataset Split}
To avoid methodological bias and data leakage, the 1,200-frame time series is partitioned into
strict non-overlapping operational windows:
\begin{itemize}
    \item \textbf{Calibration Window (Frames 0..199, 200 frames / 4.0 s):} Exclusively clean,
    stationary baseline telemetry. Used to compute reference mean vector $\boldsymbol{\mu}$,
    sample covariance $\boldsymbol{\Sigma}$, and inverse precision matrix $\boldsymbol{W} = \boldsymbol{\Sigma}^{-1}$.
    Zero attack contamination is permitted.
    \item \textbf{Test Evaluation Split (Frames 200..1199, 1,000 frames / 20.0 s):} Contains all
    four attack injection windows interspersed with unattacked recovery periods. All statistical
    detection metrics (Accuracy, Precision, Recall, F1, ROC-AUC) are evaluated on this test split.
\end{itemize}

\section{Hardware Architecture and Module Partitioning}
Figure~\ref{fig:hardware_choose} illustrates the structural partitioning between software
offline calibration and dedicated FPGA hardware execution.

\reportfigure[0.85\textwidth]{hardware_choose}{Hardware architecture selection and processing partition.}{fig:hardware_choose}

The hardware architecture (\texttt{pmu\_anomaly\_top.sv}) decomposes the anomaly detection engine
into dedicated, interacting functional blocks:
\begin{itemize}
    \item \textbf{Master FSM Controller (\texttt{pmu\_fsm\_ctrl}):} Coordinates synchronous sample
    capture, datapath handshakes, threshold evaluations, and state memory write-backs.
    \item \textbf{Mahalanobis Matrix Engine (\texttt{mahalanobis\_matrix\_engine}):} Computes spatial
    matrix-vector multiplication and quadratic dot product using dedicated DSP48E1 slices.
    \item \textbf{Two-Sided CUSUM Core (\texttt{cusum\_filter\_q15}):} Implements signed positive and
    negative recursive accumulations with zero-clamping logic.
    \item \textbf{Time-Multiplexed State Memory (\texttt{pmu\_state\_bram}):} Stores per-channel CUSUM
    accumulator states and history flags in dual-port Block RAM.
\end{itemize}

Figure~\ref{fig:rtl_schematic} displays the elaborated RTL schematic generated by Vivado
Design Suite, illustrating the inter-module signal connectivity and bus widths.

\reportfigure[0.95\textwidth]{schematic}{Elaborated top-level RTL schematic of the PMU anomaly engine.}{fig:rtl_schematic}

\section{Circuit-Level Datapath and Arithmetic Safeguards}
Figure~\ref{fig:circuit_diagram} shows the circuit-level datapath schematic, highlighting
the internal arithmetic structures and numerical protection stages.

\reportfigure[0.95\textwidth]{circuit_diagram}{Circuit-level schematic of the fixed-point arithmetic datapath.}{fig:circuit_diagram}

The datapath incorporates four critical hardware safeguards:
\begin{enumerate}
    \item \textbf{DSP48E1 Multiplier Utilization:} 16-bit signed operands multiply directly
    into 32-bit Q2.30 intermediate products using hardware DSP slices, preventing fabric logic bloat.
    \item \textbf{34-Bit Accumulator Guard Bits:} An internal 34-bit accumulator (Q4.30) provides
    2 integer guard bits ($32 + \lceil \log_2 4 \rceil = 34$), eliminating intermediate overflow
    during 4-element dot-product summations.
    \item \textbf{Convergent Half-Up Rounding:} Rescaling from 34 bits back to 16 bits adds
    $+2^{14} = \text{0x0000\_4000}$ before truncating bits $[30:15]$, eliminating negative DC bias.
    \item \textbf{Two's-Complement Saturation Logic:} Prevents negative overflow wrapping;
    excursions beyond $+0.999969$ clamp strictly to \texttt{0x7FFF}, and negative excursions clamp to \texttt{0x8000}.
\end{enumerate}

\section{Main Controller Finite-State Machine}
The operational sequencing of the hardware engine is governed by a canonical three-process
Moore Finite State Machine implemented in \texttt{rtl/pmu\_fsm\_ctrl.sv}. Process~1 executes the
sequential state register with asynchronous active-low reset; Process~2 evaluates combinational
next-state transition logic; and Process~3 generates pure Moore output strobes derived
strictly from the current state. Table~\ref{tab:fsm_states} details the complete operational
sequence, matching the actual RTL implementation.

\begin{table}[H]
\centering
\caption{FSM states and operational sequence of the PMU controller.}
\label{tab:fsm_states}
\small
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{|p{3.2cm}|p{3.8cm}|p{7.4cm}|}
\hline
\textbf{FSM State} & \textbf{Architectural Function} & \textbf{Hardware Action Executed in RTL} \\
\hline
\texttt{FSM\_IDLE} & Wait for input sample & Asserts \texttt{data\_ready = 1'b1}; awaits upstream \texttt{data\_valid} strobe from PMU stream. \\
\hline
\texttt{FSM\_CAPTURE} & Latch measurement vector & Asserts \texttt{latch\_sample\_o = 1'b1}; latches 64-bit parallel PMU telemetry vector into input pipeline. \\
\hline
\texttt{FSM\_PREPROCESS} & Mean-centering \& residual & Asserts \texttt{preprocess\_en\_o = 1'b1}; computes signed deviation residual $\boldsymbol{r} = \boldsymbol{z} - \boldsymbol{\mu}$ using calibration registers. \\
\hline
\texttt{FSM\_MAHALANOBIS} & Compute spatial distance & Asserts \texttt{mahal\_start\_o = 1'b1}; triggers 3-cycle matrix engine to compute $\boldsymbol{y} = \boldsymbol{W}\boldsymbol{r}$ and $D^2 = \boldsymbol{r}^T\boldsymbol{y}$; waits for \texttt{mahal\_done}. \\
\hline
\texttt{FSM\_CUSUM} & Update CUSUM filter & Asserts \texttt{cusum\_en\_o = 1'b1}; updates positive ($S^+$) and negative ($S^-$) sequential accumulators with zero-clamping. \\
\hline
\texttt{FSM\_DECISION} & Compare thresholds & Asserts \texttt{decision\_en\_o = 1'b1}; evaluates $D^2 \gtrless \tau^2$ and $S^+, S^- \gtrless h$; asserts global alarm if breached. \\
\hline
\texttt{FSM\_STORE\_RESULT} & Write-back state to BRAM & Asserts \texttt{bram\_we\_o = 1'b1}; writes updated channel CUSUM accumulators and status flags to time-multiplexed BRAM. \\
\hline
\texttt{FSM\_NEXT\_CHANNEL} & Channel advance / loop & Asserts \texttt{chan\_advance\_o = 1'b1}; asserts \texttt{frame\_done\_o = 1'b1} when \texttt{channel\_last} is high; loops to \texttt{CAPTURE} or \texttt{IDLE}. \\
\hline
\end{tabular}
\end{table}

\section{Mahalanobis Matrix Engine Datapath}
The Mahalanobis engine (\texttt{rtl/mahalanobis\_matrix\_engine.sv}) computes the quadratic form
$D^2 = \boldsymbol{r}^T \boldsymbol{W} \boldsymbol{r}$ over a fully pipelined 3-cycle sequence:
\begin{itemize}
    \item \textbf{Cycle 1 (Matrix-Vector Multiplication):} Four parallel row-MAC units multiply
    the 16-bit residual vector $\boldsymbol{r} = [r_1, r_2, r_3, r_4]^T$ by the $4 \times 4$
    precomputed precision matrix $\boldsymbol{W}$:
    \begin{equation}
    y_i = \sum_{j=1}^4 W_{ij} r_j, \quad i \in \{1, 2, 3, 4\}.
    \end{equation}
    Each row multiplication consumes 4 DSP multipliers operating in parallel.
    \item \textbf{Cycle 2 (Quadratic Dot Product):} The resulting intermediate vector $\boldsymbol{y}$
    is multiplied element-wise by the original residual vector $\boldsymbol{r}$:
    \begin{equation}
    D^2 = \sum_{i=1}^4 r_i y_i.
    \end{equation}
    This summation is accumulated in a 34-bit register with 2 guard bits.
    \item \textbf{Cycle 3 (Rounding \& Output Registration):} The 34-bit accumulator value is
    rounded to Q1.15 using convergent half-up rounding, saturated, registered onto the output
    port, and the completion strobe \texttt{mahal\_done} is asserted.
\end{itemize}

\section{Two-Sided CUSUM Sequential RTL Datapath}
The CUSUM core (\texttt{rtl/cusum\_filter\_q15.sv}) executes Equations~\eqref{eq:ch3_cusum_pos} and
\eqref{eq:ch3_cusum_neg} in a single clock cycle. The incoming preprocessed measurement $y_t$
is subtracted from reference mean $\nu_0$ and reference allowance $k$:
\begin{align}
\text{diff\_pos} &= (y_t - \nu_0) - k, \\
\text{diff\_neg} &= -(y_t - \nu_0) - k.
\end{align}
These differences are added to the registered accumulator values $S_{t-1}^+$ and $S_{t-1}^-$.
Dedicated combinational comparators evaluate whether the sum is less than zero; if negative,
the accumulator input is multiplexed to zero, executing instantaneous zero-clamping reset.
Parallel threshold comparators compare $S_t^+$ and $S_t^-$ against $h$, asserting the channel
alarm strobe if either threshold is crossed.

\section{Dual-Port BRAM / LUTRAM State Storage}
The anomaly engine incorporates embedded memory (\texttt{rtl/pmu\_state\_bram.sv}) to maintain CUSUM
accumulator states across successive sample frames. The per-channel state record packs 42 bits:
\begin{itemize}
    \item Positive Accumulator ($S^+$): 16 bits Q1.15.
    \item Negative Accumulator ($S^-$): 16 bits Q1.15.
    \item Channel Alarm Latch: 1 bit.
    \item Anomaly Counter: 8 bits.
    \item Channel Valid Flag: 1 bit.
\end{itemize}
When synthesized targeting dedicated primitives, Vivado infers two RAMB18E1 block RAMs because
the 42-bit packed word exceeds the 36-bit port width of a single RAMB18 block. Alternatively,
the architecture supports parameterization for distributed LUTRAM synthesis, requiring only
11 SLICEM LUTs and zero Block RAMs.

\section{Hardware Timing and Complexity Analysis}
Table~\ref{tab:hardware_timing} presents the verified cycle counts, execution latency,
line-rate throughput, and operational capacity of the hardware anomaly engine operating at
a 100~MHz clock target.

\begin{table}[H]
\centering
\caption{Hardware timing and complexity analysis.}
\label{tab:hardware_timing}
\small
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{|p{4.2cm}|p{3.2cm}|p{2.2cm}|p{1.8cm}|p{3.0cm}|}
\hline
\textbf{Timing / Complexity Parameter} & \textbf{Verification Status} & \textbf{Value} & \textbf{Unit} & \textbf{Operational Meaning} \\
\hline
System Clock Frequency ($f_{\text{clk}}$) & Design Target & 100.0 & MHz & Nominal clock period $T_{\text{clk}} = 10.0~\text{ns}$. \\
\hline
Channel Processing Latency & Verified RTL Cycle Count & 9 & Cycles & Execution time per PMU channel ($90~\text{ns}$). \\
\hline
Full 4-Channel Frame Latency & Verified RTL Cycle Count & 36 & Cycles & Total execution latency ($360~\text{ns} = 0.36~\mu\text{s}$). \\
\hline
Maximum Processing Throughput & Architectural Calculation & 2.78 & MSamples/s & 2,777,777 measurement frames per second. \\
\hline
PMU Standard Period (IEEE C37.118) & Standard Specification & 20.0 & ms & Transmission PMU frame arrival (50~Hz). \\
\hline
Hardware Idle Duty Cycle & Analytical Ratio & 99.9982 & \% & Core remains idle for 19.99964~ms per frame. \\
\hline
Time-Multiplexed PMU Capacity & Architectural Calculation & 55,555 & Streams & Single FPGA core capacity for 50~Hz PMUs. \\
\hline
Worst Negative Slack (WNS) & Estimated Post-Synthesis & Pending & ns & Synthesis clean; pending post-route sign-off. \\
\hline
\end{tabular}
\end{table}

\section{Target FPGA Platform: Artix-7 XC7A200T-FBG676-2}
The AMD/Xilinx Artix-7 XC7A200T device serves as the primary implementation target.
The device characteristics include:
\begin{itemize}
    \item Device Part: \texttt{xc7a200tfbg676-2}.
    \item Logic Slices: 33,650 (134,600 LUT6, 269,200 Registers).
    \item DSP48E1 Multipliers: 740 slices.
    \item Block RAM: 730 RAMB18E1 equivalents (13,140 Kb).
    \item Bonded IOBs: 400 user I/O pins.
\end{itemize}

\section{Verification Strategy and Testbench Hierarchy}
The verification hierarchy comprises two complementary layers:
\begin{enumerate}
    \item \textbf{Unit-Level Testbenches:} Standalone testbenches verify individual modules:
    \texttt{tb\_fixed\_point\_multiplier.sv} verifies rounding and saturation corner cases;
    \texttt{tb\_mahalanobis\_matrix.sv} tests matrix-vector dot products against precomputed
    algebraic vectors; \texttt{tb\_cusum\_filter.sv} tests positive/negative drift clamping.
    \item \textbf{System-Level Testbench (\texttt{tb\_pmu\_anomaly\_top}):} Feeds the entire 1,200-frame
    telemetry sequence from \texttt{pmu\_telemetry.csv} through the top-level RTL entity, logs hardware
    alerts and scores to \texttt{rtl\_output.csv}, and performs automated assertion checks against the
    Python golden model.
\end{enumerate}
"""

print("Chapter 4 module loaded.")
