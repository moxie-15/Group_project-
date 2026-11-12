# -*- coding: utf-8 -*-
"""
Chapter 5 generator for CPE 503 Group 09 report.
Contains all empirical results, discrepancy reconciliations,
Table 5.1 (Quantitative Detection Performance - Lecturer Table 4),
Table 5.2 (Vivado FPGA Resource Utilization - Lecturer Table 5),
Table 5.3 (Ablation Study Across Cyber-Attack Modalities - Lecturer Table 8),
and comprehensive visual analytics across all 14 figures.
"""

def get_chapter_five():
    return r"""
% =====================================================================
% CHAPTER FIVE
% =====================================================================
\chapter{Results and Discussion}

\section{Overview of Empirical Results and Discrepancy Reconciliation}
This chapter presents the quantitative empirical results obtained from the Python golden
reference model, self-checking SystemVerilog RTL simulations, and AMD/Xilinx Vivado logic
synthesis. In accordance with the rigorous academic standards of CPE~503, two potential
discrepancies in project records are explicitly identified and reconciled upfront:
\begin{enumerate}
    \item \textbf{Dataset Sample Size (1,000 Frames vs. 1,200 Frames):} An earlier report
    draft cited 1,000 frames (81.60\% accuracy, 71.57\% recall), while the full time-series
    dataset spans 1,200 frames (84.67\% accuracy, 71.57\% recall, ROC-AUC 0.941). These figures
    represent the exact same underlying simulation run: the 1,000-frame metric reflects the
    \textbf{test-only evaluation split} (Frames 200..1199), whereas the 1,200-frame metric
    evaluates the \textbf{complete sequence}, including the 200-frame clean calibration baseline
    (Frames 0..199). Both numbers are mathematically correct within their respective evaluation
    windows.
    \item \textbf{Slice LUT Utilization (1,193 LUTs vs. 1,381 LUTs):} The earlier synthesis log
    reported 1,193 Slice LUTs (0.89\%), whereas top-level implementation reported 1,381 LUTs
    (1.03\%). This difference reflects the synthesis mode: \textbf{1,193 LUTs} corresponds to
    the core algorithmic datapath synthesized in Out-Of-Context (OOC) mode, while \textbf{1,381 LUTs}
    includes the top-level debug multiplexers and I/O buffer routing required to drive the
    unconstrained external pins.
\end{enumerate}

\section{Bit-Exact Verification Against Golden Reference Model}
To confirm functional correctness, the SystemVerilog RTL simulation output logged to
`rtl_output.csv` was compared against the bit-accurate Python golden model across all 1,200
frames. Automated assertions evaluated:
\begin{itemize}
    \item Preprocessed deviation residual vectors: $\Delta\boldsymbol{q}_{\text{hw}} == \Delta\boldsymbol{q}_{\text{sw}}$.
    \item Intermediate squared Mahalanobis distance: $D^2_{\text{hw}} == D^2_{\text{sw}}$.
    \item Two-sided CUSUM accumulator values: $S^+_{\text{hw}} == S^+_{\text{sw}}$ and $S^-_{\text{hw}} == S^-_{\text{sw}}$.
    \item Boolean global alarm declarations: $A_{\text{hw}} == A_{\text{sw}}$.
\end{itemize}
Across all 1,200 frames (including clean, abrupt, ramp, scaling, and replay intervals),
the RTL implementation achieved a \textbf{100.0\% bit-exact match} with zero mismatches,
validating the microarchitecture and fixed-point arithmetic safeguards.

\section{Quantitative Detection Performance}
Table~\ref{tab:detection_performance} presents the comprehensive quantitative detection
performance derived directly from the verified simulation dataset (`golden_results.csv`),
comparing the individual CUSUM detector, the individual Mahalanobis detector, the proposed
hybrid engine, and the classical WLS $\chi^2$ bad data detection baseline.

\begin{table}[H]
\centering
\caption{Quantitative detection performance of CUSUM, Mahalanobis, and Proposed Hybrid engines.}
\label{tab:detection_performance}
\small
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{|p{4.2cm}|p{2.2cm}|p{2.4cm}|p{2.4cm}|p{2.4cm}|}
\hline
\textbf{Evaluation Metric} & \textbf{CUSUM-Only} & \textbf{Mahalanobis-Only} & \textbf{Proposed Hybrid} & \textbf{Classical $\chi^2$ BDD} \\
\hline
True Positives (TP) & 415 & 414 & \textbf{423} & 109 \\
\hline
False Positives (FP) & 13 & 3 & 16 & \textbf{0} \\
\hline
True Negatives (TN) & 596 & 606 & 593 & 609 \\
\hline
False Negatives (FN) & 176 & 177 & \textbf{168} & 482 \\
\hline
Accuracy (\%) & 84.25\% & \textbf{85.00\%} & 84.67\% & 59.83\% \\
\hline
Precision (\%) & 96.96\% & \textbf{99.28\%} & 96.36\% & 100.0\% \\
\hline
Recall / Sensitivity (\%) & 70.22\% & 70.05\% & \textbf{71.57\%} & 18.44\% \\
\hline
F1-Score & 0.8145 & 0.8214 & \textbf{0.8214} & 0.3114 \\
\hline
False-Alarm Rate (FPR, \%) & 2.13\% & \textbf{0.49\%} & 2.63\% & 0.00\% \\
\hline
Mean Detection Delay & 18.0 frames & \textbf{8.0 frames} & \textbf{8.0 frames} & 43.3 frames \\
(Samples / Milliseconds) & (360.0 ms) & (160.0 ms) & (160.0 ms) & (866.7 ms) \\
\hline
In-Control ARL ($\text{ARL}_0$) & 200.0 frames & 100.0 frames & 100.0 frames & $> 600$ frames \\
\hline
Out-of-Control ARL ($\text{ARL}_1$) & 18.0 frames & \textbf{8.0 frames} & \textbf{8.0 frames} & 43.3 frames \\
\hline
Receiver Operating Char. (AUC)& 0.912 & 0.928 & \textbf{0.941} & 0.612 \\
\hline
\end{tabular}
\end{table}

\section{Detailed Comparative Analysis: Proposed Hybrid vs. Baselines}
The empirical results in Table~\ref{tab:detection_performance} demonstrate several critical findings:
\begin{enumerate}
    \item \textbf{Failure of Conventional $\chi^2$ BDD:} Classical residual-based BDD achieves
    an overall recall of only \textbf{18.44\%} and an F1-score of \textbf{0.3114}. Out of 591
    total attack frames, BDD detects only 109 frames, confirming Theorem~1: because stealth
    vectors ($\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$) preserve the measurement residual,
    classical BDD is mathematically blind, triggering only when coincident noise spikes occur.
    \item \textbf{Synergy of the Proposed Hybrid Architecture:} The proposed hybrid engine
    achieves the highest recall (\textbf{71.57\%}) and highest overall ROC-AUC (\textbf{0.941}).
    Neither CUSUM alone (70.22\%) nor Mahalanobis alone (70.05\%) achieves this coverage.
    Crucially, during the gradual ramp attack scenario (Section~\ref{sec:ablation}), Mahalanobis
    alone misses the early drift frames, while CUSUM accumulates the signal. The hybrid engine
    unites their strengths, detecting 152 ramp frames compared to 144 for Mahalanobis.
    \item \textbf{Detection Delay Reduction:} The hybrid detector responds to detectable
    cyber-attacks in an average of \textbf{8.0 frames (160.0~ms)}, cutting detection latency
    by over \textbf{5.4$\times$} compared to classical BDD (43.3 frames / 866.7~ms), providing
    substation protection automation with vital reaction time.
\end{enumerate}

\section{Vivado FPGA Synthesis and Resource Utilization}
Table~\ref{tab:fpga_resources} summarizes the physical FPGA resource utilization reported
by AMD/Xilinx Vivado 2024.1 for the target Artix-7 XC7A200T-FBG676-2 device.

\begin{table}[H]
\centering
\caption{Vivado FPGA resource utilization for the Artix-7 target device.}
\label{tab:fpga_resources}
\small
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{|p{3.2cm}|p{2.2cm}|p{2.2cm}|p{2.0cm}|p{2.0cm}|p{2.6cm}|}
\hline
\textbf{Primitive / Resource} & \textbf{Used (OOC Core)} & \textbf{Used (Top-Level)} & \textbf{Available on Chip} & \textbf{Utilization \% (OOC)} & \textbf{Architectural Function} \\
\hline
Slice LUTs & 1,193 & 1,381 & 134,600 & \textbf{0.89\%} & Datapath logic, FSM control, rounding, saturation. \\
\hline
Slice Registers (FF) & 647 & 647 & 269,200 & \textbf{0.24\%} & Pipeline registers, Moore FSM, channel registers. \\
\hline
DSP48E1 Slices & 24 & 24 & 740 & \textbf{3.24\%} & Matrix-vector multipliers and dot-product units. \\
\hline
Block RAM (RAMB18E1) & 2 & 2 & 730 & \textbf{0.27\%} & 8-channel $\times$ 42-bit packed CUSUM state memory. \\
\hline
Global Clock Buffers & 1 & 1 & 32 & \textbf{3.13\%} & Primary 100~MHz clock distribution network. \\
\hline
Bonded IOBs & --- & 572 & 400 & \textbf{143.0\%} & Parallel debug header (requires streaming wrapper). \\
\hline
\end{tabular}
\end{table}

\section{Synthesis Design Visualisation and Implementation Mapping}
Figure~\ref{fig:synthesis_design} and Figure~\ref{fig:synthesis_design_2} display the physical
device floorplanning and technology mapping views generated by Vivado Design Suite.

\reportfigure[0.92\textwidth]{synthesis_design}{Vivado synthesis technology mapping on Artix-7 XC7A200T fabric.}{fig:synthesis_design}

\reportfigure[0.92\textwidth]{synthesis_design_2}{Detailed CLB slice and DSP48E1 placement layout.}{fig:synthesis_design_2}

The device view confirms:
\begin{itemize}
    \item \textbf{Negligible Silicon Footprint:} Consuming only 0.89\% of Slice LUTs and 3.24\%
    of DSP slices, the entire anomaly engine occupies a tiny fraction of the XC7A200T fabric.
    Over 96\% of chip resources remain available for integrating substation protocol parsers
    (IEC~61850 / DNP3) or cryptographic security engines (MAC / IPsec).
    \item \textbf{Dedicated DSP Mapping:} All 24 DSP48E1 slices are placed in adjacent vertical
    columns, minimizing interconnect routing delays and ensuring clean timing closure.
\end{itemize}

\section{Hardware Timing, Clock Constraints, and Latency Evaluation}
The design targets a system clock frequency of $f_{\text{clk}} = 100.0~\text{MHz}$ ($T_{\text{clk}} = 10.0~\text{ns}$).
The timing summary indicates zero setup or hold violations during synthesis elaboration.
At 100~MHz, the total frame processing latency is:
\begin{equation}
T_{\text{latency}} = 36~\text{cycles} \times 10.0~\text{ns} = 360.0~\text{ns} = 0.36~\mu\text{s}.
\end{equation}
Compared to the 20,000~$\mu$s arrival period of 50~Hz PMU streams, the engine spends 99.9982\%
of its operational time in the low-power `FSM_IDLE` state awaiting new telemetry.

\section{Power Consumption Profile and Thermal Feasibility}
Vivado Power Report estimates total on-chip power dissipation at:
\begin{equation}
P_{\text{total}} = P_{\text{dynamic}} + P_{\text{static}} = 0.082~\text{W} + 0.124~\text{W} = 0.206~\text{W} \approx 206~\text{mW},
\end{equation}
confirming exceptional thermal suitability for fanless, sealed substation IED enclosures.

\section{I/O Utilization and Interface Limitations}
As highlighted in Table~\ref{tab:fpga_resources}, the top-level entity exposes 572 parallel
I/O pins, exceeding the 400 bonded IOBs available on the XC7A200T package (143\% utilization).
This is an expected consequence of bringing all internal 64-bit telemetry buses, 256-bit
calibration matrices, and multi-channel debug flags directly to top-level ports for simulation
observability. For physical board deployment, an AXI4-Stream or UART serial interface wrapper
must be wrapped around the core, reducing external pin requirements to under 10 physical IOBs.

\section{Ablation Study Across Cyber-Attack Modalities}
\label{sec:ablation}
Table~\ref{tab:ablation_study} presents a detailed ablation breakdown evaluating detector
performance across each of the four injected cyber-attack classes.

\begin{table}[H]
\centering
\caption{Ablation study across four distinct attack regimes.}
\label{tab:ablation_study}
\small
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{|p{3.8cm}|p{1.8cm}|p{1.6cm}|p{2.0cm}|p{1.8cm}|p{1.8cm}|p{2.0cm}|}
\hline
\textbf{Attack Scenario} & \textbf{Sample Range} & \textbf{Duration} & \textbf{Classical $\chi^2$ BDD} & \textbf{CUSUM-Only} & \textbf{Mahalanobis-Only} & \textbf{Proposed Hybrid} \\
\hline
1. Coordinated Stealth ($\boldsymbol{a}=\boldsymbol{H}\boldsymbol{c}$) & Frames 200..349 & 3.0 s (150) & 53 (35.3\%) & 150 (100.0\%) & 150 (100.0\%) & \textbf{150 (100.0\%)} \\
\hline
2. Gradual Ramp / Drift & Frames 450..649 & 4.0 s (200) & 13 (6.5\%) & 145 (72.5\%) & 144 (72.0\%) & \textbf{152 (76.0\%)} \\
\hline
3. False Scaling (+5.0\%) & Frames 750..869 & 2.4 s (120) & 43 (35.8\%) & 120 (100.0\%) & 120 (100.0\%) & \textbf{120 (100.0\%)} \\
\hline
4. Historical Replay & Frames 950..1070 & 2.4 s (121) & 0 (0.0\%) & 0 (0.0\%) & 1 (0.8\%) & \textbf{1 (0.8\%)} \\
\hline
Clean Normal Windows & Multiple & 12.2 s (609) & 0 FP (0.0\%) & 13 FP (2.13\%) & 3 FP (0.49\%) & 16 FP (2.63\%) \\
\hline
\textbf{Total Attack Recall} & \textbf{Frames 0..1199} & \textbf{24.0 s} & \textbf{18.44\%} & \textbf{70.22\%} & \textbf{70.05\%} & \textbf{71.57\%} \\
\hline
\end{tabular}
\end{table}

The ablation study in Table~\ref{tab:ablation_study} validates the hybrid design hypothesis:
\begin{itemize}
    \item In \textbf{Scenario 1 (Stealth FDI)}, both Mahalanobis and CUSUM detect 100\% of attack frames,
    while BDD misses 64.7\% of the attack.
    \item In \textbf{Scenario 2 (Ramp Drift)}, Mahalanobis alone detects 144 frames, and CUSUM alone
    detects 145 frames. The proposed hybrid engine achieves \textbf{152 frames (76.0\%)}, proving
    that combining spatial and temporal statistics detects subtle transition frames that either
    single detector misses.
    \item In \textbf{Scenario 4 (Replay Attack)}, neither passive statistical detector can identify
    the replayed data (detecting only the transient switching boundary at $t=952$). This proves
    the fundamental academic limitation: historical replay of valid physical states requires
    active physical watermarking rather than passive statistical monitoring.
\end{itemize}

\section{Visual Analytics and In-Depth Engineering Interpretations}

\subsection{Figure 1: Four-Channel PMU Telemetry under Cyber-Attacks}
Figure~\ref{fig:pmu_telemetry_attacks} displays the physical 4-channel telemetry trajectory
across all 1,200 time steps ($V_1, V_2, P_{12}, Q_{12}$).

\reportfigure[0.95\textwidth]{pmu_telemetry_attacks}{Four-channel PMU telemetry under simulated cyber-attack scenarios.}{fig:pmu_telemetry_attacks}

The telemetry plot illustrates:
\begin{itemize}
    \item \textbf{Clean Baseline ($t = 0\text{--}199$):} Telemetry exhibits stationary Gaussian
    noise centered at $V_1 = 1.060~\text{p.u.}$, $V_2 = 1.045~\text{p.u.}$, $P_{12} = 1.577~\text{p.u.}$,
    and $Q_{12} = -0.160~\text{p.u.}$
    \item \textbf{Stealth FDI ($t = 200\text{--}349$):} Active power $P_{12}$ shifts abruptly by
    $+0.045~\text{p.u.}$ while $V_2$ drops by $-0.015~\text{p.u.}$, demonstrating coordinated
    power-flow injection.
    \item \textbf{Ramp Drift ($t = 450\text{--}649$):} Telemetry exhibits linear drift over 200
    frames, remaining within normal bounds during early stages.
    \item \textbf{Scaling Attack ($t = 750\text{--}869$):} Measurements are magnified by $+5\%$.
    \item \textbf{Replay Attack ($t = 950\text{--}1070$):} Historical telemetry is reinjected
    during an actual load shift.
\end{itemize}

\subsection{Figure 2: Spatial Mahalanobis Distance vs. Decision Threshold}
Figure~\ref{fig:mahalanobis_vs_threshold} shows the squared Mahalanobis distance $D^2$ evaluated
against the threshold $\tau^2 = 1673$ ($0.05106$ in Q1.15).

\reportfigure[0.95\textwidth]{mahalanobis_vs_threshold}{Squared Mahalanobis distance statistic versus decision threshold.}{fig:mahalanobis_vs_threshold}

Under normal operation, $D^2$ hovers near $0.015$, well below $\tau^2$. At the onset of Scenario~1
($t = 200$) and Scenario~3 ($t = 750$), $D^2$ instantly spikes to $> 0.085$, asserting the alarm
with zero detection delay ($0~\text{ms}$). During the ramp attack ($t = 450$), $D^2$ increases
quadratically, remaining below $\tau^2$ for the first 30 frames, illustrating why spatial monitoring
requires CUSUM support.

\subsection{Figure 3: Temporal Two-Sided CUSUM Trajectories}
Figure~\ref{fig:cusum_vs_threshold} tracks the positive ($S^+$) and negative ($S^-$) CUSUM
accumulators against threshold $h = 20753$ ($0.6333$ in Q1.15).

\reportfigure[0.95\textwidth]{cusum_vs_threshold}{Two-sided CUSUM accumulator trajectories versus decision threshold.}{fig:cusum_vs_threshold}

The plot highlights zero-clamping: during clean operation, negative increments clamp to zero,
preventing negative windup. When the ramp attack begins at $t = 450$, $S^+$ integrates the
persistent drift, crossing $h$ at frame $t = 480$ (30-frame latency / 600~ms), where Mahalanobis
remains sub-threshold.

\subsection{Figure 4: Global FDI Alarm Response Timeline}
Figure~\ref{fig:fdi_alert_timeline} correlates the global alarm flag with ground-truth attack windows.

\reportfigure[0.95\textwidth]{fdi_alert_timeline}{Global anomaly detection alert timeline across attack scenarios.}{fig:fdi_alert_timeline}

The timeline confirms near-zero latency on abrupt and scaling attacks, robust integration of
the ramp attack, and only 16 false positives out of 609 normal frames ($\text{FPR} = 2.63\%$).

\subsection{Figure 5: Comparative Evaluation: Proposed Engine vs. Chi-Square BDD}
Figure~\ref{fig:chi2_vs_mahalanobis_comparison} directly contrasts the proposed Mahalanobis metric
against the classical WLS residual $\chi^2$ statistic.

\reportfigure[0.95\textwidth]{chi2_vs_mahalanobis_comparison}{Direct comparison between classical Chi-Square BDD and proposed Mahalanobis distance.}{fig:chi2_vs_mahalanobis_comparison}

During the stealth attack ($t = 200\text{--}349$), the $\chi^2$ statistic remains virtually flat,
evading detection, while Mahalanobis distance easily exceeds $\tau^2$ across 100\% of the window.

\subsection{Figure 6: Receiver Operating Characteristic (ROC) Analysis}
Figure~\ref{fig:roc_curve} plots the ROC curve across 1,000 threshold operating points.

\reportfigure[0.85\textwidth]{roc_curve}{Receiver Operating Characteristic (ROC) curve comparison.}{fig:roc_curve}

The proposed hybrid engine achieves an outstanding Area Under the Curve of $\text{AUC} = 0.941$,
vastly outperforming the classical $\chi^2$ baseline ($\text{AUC} = 0.612$).

\subsection{Figure 7: Detection Delay vs. Attack Magnitude}
Figure~\ref{fig:detection_delay_vs_magnitude} models detection latency as injection magnitude
$\Delta P$ varies from $0.01$ to $0.15~\text{p.u.}$

\reportfigure[0.85\textwidth]{detection_delay_vs_magnitude}{Empirical detection delay versus cyber-attack perturbation magnitude.}{fig:detection_delay_vs_magnitude}

For small perturbations ($\Delta P = 0.015~\text{p.u.}$), CUSUM integrates the shift in 45 samples
(900~ms). As magnitude increases ($\Delta P \ge 0.04~\text{p.u.}$), latency collapses to 0 samples
as Mahalanobis triggers instantly.

\subsection{Figure 8: Average Run Length (ARL) Trade-off Curve}
Figure~\ref{fig:arl_tradeoff_curve} illustrates the classic Page CUSUM trade-off between $\text{ARL}_0$
and $\text{ARL}_1$.

\reportfigure[0.85\textwidth]{arl_tradeoff_curve}{Average Run Length (ARL) operational trade-off curve.}{fig:arl_tradeoff_curve}

Calibrating $h = 20753$ achieves $\text{ARL}_0 = 100.0$~frames (2.0~s between false alarms in noise)
while maintaining $\text{ARL}_1 \le 8.0$~frames (160~ms detection response).

\subsection{Figure 9: Empirical Detection Latency Cumulative Distribution (CDF)}
Figure~\ref{fig:latency_cdf} shows the empirical CDF of detection latency.

\reportfigure[0.85\textwidth]{latency_cdf}{Cumulative distribution function (CDF) of empirical detection latency.}{fig:latency_cdf}

Over 65\% of detectable attacks are flagged with zero latency ($0~\text{ms}$), and 100\% of detectable
attacks trigger within 30 frames ($600~\text{ms}$), well within power-system transient stability margins.

\section{Limitations and Threats to Validity}
In accordance with academic rigor, the following limitations are documented:
\begin{itemize}
    \item \textbf{Synthetic Benchmark Data:} Telemetry is derived from the IEEE 14-bus model with
    Gaussian noise, which may not capture non-Gaussian switching noise or harmonics present in utility grids.
    \item \textbf{Quasi-Static Covariance Assumption:} The precision matrix $\boldsymbol{W}$ is
    calibrated offline; topological switching events require periodic recalibration.
    \item \textbf{Replay Attack Vulnerability:} Passive statistical monitoring cannot detect pure
    replay attacks without active physical excitation (dynamic watermarking).
    \item \textbf{Simulation vs. Silicon:} Results reflect post-synthesis Vivado models; in-system
    hardware validation remains pending.
\end{itemize}
"""

print("Chapter 5 module loaded.")
