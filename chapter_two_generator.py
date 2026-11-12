# -*- coding: utf-8 -*-
"""
Concise Chapter 2 generator for CPE 503 Group 09 report.
Maintains the exact 14-section sequence, Table 2.1, Table 2.2, and academic rigor,
condensed to 4-5 pages maximum.
"""

def get_chapter_two():
    return r"""
% =====================================================================
% CHAPTER TWO
% =====================================================================
\chapter{Literature Review}

\section{Introduction}
Modern smart electrical grids integrate advanced communication, digital sensing, and automated
control platforms with traditional high-voltage physical assets. While Phasor Measurement Units
(PMUs) and Wide Area Monitoring Systems (WAMS) enable real-time situational awareness, their
reliance on networked communication introduces severe cybersecurity vulnerabilities. Among these,
False Data Injection (FDI) attacks deliberately manipulate sensor telemetry to deceive Power
System State Estimation (PSSE) while evading conventional bad-data detection.

To address this challenge, researchers have explored multivariate statistical analysis and
sequential change-point monitoring. Mahalanobis distance evaluates instantaneous cross-channel
correlations, while the Cumulative Sum (CUSUM) algorithm integrates subtle persistent shifts over
time. Translating these algorithms into digital hardware such as Field-Programmable Gate Arrays
(FPGAs) provides deterministic microsecond execution, but requires careful fixed-point scaling
to manage finite-precision effects. This chapter reviews the architectural, statistical, and
hardware foundations of smart-grid FDI anomaly detection, culminating in a critical analysis of
existing approaches and an explicit research gap.

\section{Smart Grid Architecture and Operation}

\subsection{Overview and Conceptual Domains}
A smart grid functions as an interconnected cyber-physical system where physical electricity flows
are continuously supervised by digital information networks. The National Institute of Standards
and Technology (NIST) conceptual model \cite{nist2014framework} identifies seven functional domains,
as summarized in Table~\ref{tab:smartgrid_domains}.

\begin{table}[htbp]
\centering
\caption{Major domains of the NIST smart grid conceptual model.}
\label{tab:smartgrid_domains}
\renewcommand{\arraystretch}{1.2}
\small
\begin{tabular}{|p{3.0cm}|p{5.0cm}|p{6.0cm}|}
\hline
\textbf{Domain} & \textbf{Primary Function} & \textbf{Typical Components or Activities} \\
\hline
Bulk Generation & Large-scale electricity generation & Power plants, renewable farms, generation control \\
\hline
Transmission & Long-distance bulk power transfer & High-voltage lines, substations, PMUs, relays \\
\hline
Distribution & Local electricity delivery to end users & Feeders, reclosers, transformers, microgrids \\
\hline
Operations & Network supervision and control & SCADA, Energy Management Systems (EMS), WAMS \\
\hline
Markets & Economic energy exchange & Trading platforms, aggregators, clearing houses \\
\hline
Service Providers & Third-party utility support & Billing, data analytics, customer services \\
\hline
Customers & Energy consumption and local generation & Smart meters, EV chargers, rooftop solar arrays \\
\hline
\end{tabular}
\end{table}

\subsection{Power Flows and Data Integrity}
Transmission networks transmit electric energy across geographically distributed buses. Monitoring
relies on voltage, current, and active/reactive power measurements to estimate network operating
states. Because supervisory decisions directly impact physical grid stability, measurement
integrity is paramount: corrupted telemetry can induce erroneous generation redispatch, line
tripping, or cascading outages.

\section{Cybersecurity in Smart Grid Systems}
In power system operational technology (OT), the classic CIA triad prioritizes \textbf{Availability}
and \textbf{Integrity} over \textbf{Confidentiality} \cite{nist80082}. Telemetry streams must arrive
deterministically at 50~Hz (every 20~ms) to drive protection routines. Attack vectors include
substation LAN intrusion, unencrypted protocol tampering (DNP3, Modbus, IEC 60870-5-104), and
GPS clock spoofing. While standards such as NISTIR 7628 \cite{nist7628,nist7628r1} and IEC 62443
prescribe perimeter defenses, secondary statistical anomaly detection engines inside substations
remain essential to counter internal or stealthy network breaches.

\section{False Data Injection Attacks}
Let nominal telemetry be $\boldsymbol{z} = \boldsymbol{H}\boldsymbol{x} + \boldsymbol{e}$. In an FDI
attack, the adversary injects an additive perturbation: $\boldsymbol{z}_a = \boldsymbol{z} + \boldsymbol{a}$.
As proven by Liu, Ning, and Reiter \cite{liu2009}, if the adversary constructs the attack along the
measurement Jacobian:
\begin{equation}
\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c},
\end{equation}
where $\boldsymbol{c}$ is an arbitrary state bias, the resulting measurement residual $\boldsymbol{r}_a$
remains \textbf{strictly invariant}, rendering the attack unobservable to state estimation.
Depending on execution temporal profiles, FDI attacks manifest as abrupt step injections, gradual
ramps, multi-channel scaling, or historical replay. Crucially, detectability is not automatic: it
depends on monitored physical quantities, topological coupling, and injection magnitude relative to noise.

\section{Conventional Bad-Data Detection Techniques}
Conventional state estimation computes the Weighted Least-Squares (WLS) state estimate
$\hat{\boldsymbol{x}} = (\boldsymbol{H}^T\boldsymbol{R}^{-1}\boldsymbol{H})^{-1}\boldsymbol{H}^T\boldsymbol{R}^{-1}\boldsymbol{z}$
and evaluates the chi-square residual test $J(\hat{\boldsymbol{x}}) = \boldsymbol{r}^T\boldsymbol{R}^{-1}\boldsymbol{r} \lessgtr \gamma_{\chi^2}$
\cite{abur2004}. Under stealth FDI ($\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$):
\begin{equation}
\boldsymbol{r}_a = \boldsymbol{z}_a - \boldsymbol{H}\hat{\boldsymbol{x}}_a = (\boldsymbol{z} + \boldsymbol{H}\boldsymbol{c}) - \boldsymbol{H}(\hat{\boldsymbol{x}} + \boldsymbol{c}) = \boldsymbol{r}.
\end{equation}
Because the post-attack residual $\boldsymbol{r}_a$ is mathematically identical to pre-attack
residual $\boldsymbol{r}$, classical $\chi^2$ and Largest Normalized Residual (LNR) tests fail
completely, establishing the necessity for alternative statistical features.

\section{Statistical Anomaly Detection}
Power grid variables ($V_1, V_2, P_{12}, Q_{12}$) are physically coupled by Kirchhoff's laws and line
impedance. Univariate limit checkers fail against coordinated attacks whose elements remain within
individual bounds. Multivariate monitoring evaluates joint probability density functions, exploiting
cross-channel correlations to flag anomalies. Effective defense requires addressing both spatial
cross-correlation (instantaneous coherence) and temporal persistence (evidence accumulation).

\section{Mahalanobis Distance}
The Mahalanobis distance \cite{mahalanobis1936} measures statistical divergence from a calibrated
baseline $(\boldsymbol{\mu}, \boldsymbol{\Sigma})$:
\begin{equation}
D^2 = (\boldsymbol{q} - \boldsymbol{\mu})^T \boldsymbol{\Sigma}^{-1} (\boldsymbol{q} - \boldsymbol{\mu}) \sim \chi^2_d.
\end{equation}
By rotating deviations into principal axes and weighting by inverse variance, $D^2$ instantly
detects coordinate-conforming injections ($\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$) that
violate local voltage-power correlations. However, Mahalanobis distance evaluates single snapshots,
making it blind to subtle, gradual ramp drifts that remain within instantaneous confidence ellipsoids.

\section{CUSUM Sequential Change Detection}
Page's Cumulative Sum (CUSUM) test \cite{page1954} integrates deviations across time. The two-sided
recursive formulation maintains positive and negative accumulators \cite{montgomery2019,huang2016}:
\begin{equation}
S_n^+ = \max(0, S_{n-1}^+ + (y_n - \nu_0) - k), \quad S_n^- = \max(0, S_{n-1}^- - (y_n - \nu_0) - k).
\end{equation}
Zero-clamping prevents negative windup during normal operation, allowing instantaneous reaction upon
attack onset. Setting allowance $k = \delta/2$ suppresses Gaussian noise, while threshold $h$
governs the operational trade-off between false-alarm rate ($\text{ARL}_0$) and detection delay ($\text{ARL}_1$).
CUSUM excels at integrating slow ramps, but exhibits multi-frame lag on abrupt shifts.

\section{FPGA-Based Embedded System Implementation}
Substation automation requires line-rate telemetry inspection. Under IEEE~C37.118, PMUs report every
20~ms ($50~\text{Hz}$). General-purpose CPUs and GPUs introduce non-deterministic operating system
jitter and excessive power ($> 100~\text{W}$). In contrast, FPGAs (such as the AMD/Xilinx Artix-7
XC7A200T \cite{artix7ds}) provide deterministic sub-microsecond latency, low power ($< 2~\text{W}$),
and dedicated DSP48E1 arithmetic slices that execute pipelined matrix-vector operations with zero logic bloat.

\section{Fixed-Point Arithmetic and Q-Format Representation}
Floating-point units incur heavy resource and latency penalties. This design adopts a signed
\textbf{Q1.15} fixed-point format (1 sign bit, 15 fractional bits, dynamic range $[-1.0, +0.99997]$),
yielding a theoretical SQNR of $92.07~\text{dB}$. To eliminate intermediate overflow during 4-element
dot products, internal accumulators incorporate 2 guard bits (\textbf{34-bit Q4.30}). Convergent
$+2^{14}$ half-up rounding eliminates DC bias, and saturation clamping prevents two's-complement overflow.

\section{Review of Related Empirical Studies}
Recent literature highlights distinct research directions. Huang \textit{et al.} \cite{huang2016}
and Kumar \textit{et al.} \cite{kumar2022} evaluated CUSUM for gradual drifts, but evaluated
channels independently in software. Kurt \textit{et al.} \cite{kurt2020} demonstrated a 94.2\%
detection rate using decentralized Mahalanobis distance on IEEE 30-bus, but noted high miss rates on
slow drifts. Musleh \textit{et al.} \cite{musleh2023} deployed LSTM autoencoders, achieving 91.4\%
accuracy at the cost of 52~ms inference latency on high-end GPUs. Cui \textit{et al.} \cite{cui2024}
implemented statistical PCA on a multicore DSP, achieving 12~ms latency. Zhang \textit{et al.} \cite{zhang2024}
demonstrated FPGA synchrophasor processing, but restricted evaluation to random noise dropouts.

\section{Comparative Analysis of Existing Approaches}
Table~\ref{tab:priorwork} compares representative published works with the proposed architecture.

\begin{table}[H]
\centering
\caption{Comparison of related works in smart grid FDI anomaly detection.}
\label{tab:priorwork}
\small
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{|p{2.6cm}|p{2.4cm}|p{2.2cm}|p{3.2cm}|p{3.6cm}|}
\hline
\textbf{Author / Year} & \textbf{Detection Method} & \textbf{Platform} & \textbf{Reported Performance} & \textbf{Primary Limitation} \\
\hline
Liu, Ning \& Reiter (2009) \cite{liu2009} & Classical Bad-Data Detection (WLS / $\chi^2$) & Software (MATLAB) & Evaded by $\boldsymbol{a}=\boldsymbol{H}\boldsymbol{c}$ (0\% stealth detection) & Completely blind to coordinated stealth FDI; residual $\boldsymbol{r}$ is invariant. \\
\hline
Huang \textit{et al.} (2016) \cite{huang2016} & Adaptive Cumulative Sum (CUSUM) & Software (MATLAB) & $\text{ARL}_0 = 200$, $\text{ARL}_1 \approx 15$ steps on slow drift & Evaluates channels independently; misses spatial cross-correlation; software latency. \\
\hline
Kurt, Y\i lmaz \& Wang (2020) \cite{kurt2020} & Decentralized Mahalanobis Distance & Software (Python, IEEE 30-bus) & 94.2\% detection rate on abrupt FDI; sub-second & Evaluates single snapshots without memory; blind to slow ramp drifts below threshold. \\
\hline
Musleh, Chen \& Dong (2023) \cite{musleh2023} & Deep Learning (LSTM Autoencoder) & Software / GPU (PyTorch, RTX GPU) & 91.4\% accuracy, F1 = 0.897 on IEEE 14-bus & Latency $> 52$~ms; high power ($> 150$~W); black box lacking statistical guarantees. \\
\hline
Cui, Han \& Zou (2024) \cite{cui2024} & Statistical PCA + Chi-Square & Embedded DSP (TI TMS320C6678) & 88.2\% detection rate; 12~ms latency & High power ($> 10$~W); floating-point bottleneck; vulnerable to stealth subspace FDI. \\
\hline
\textbf{This Work (Group 9, 2026)} & \textbf{Dual-Layer Mahalanobis + Two-Sided CUSUM} & \textbf{AMD/Xilinx Artix-7 FPGA (XC7A200T)} & \textbf{84.67\% accuracy, 96.36\% precision, 71.57\% recall, F1 = 0.8214, 360~ns latency} & Fixed-point precision bounded; unobservable replay attacks require active physical watermarking. \\
\hline
\end{tabular}
\end{table}

\section{Identified Research Gap}
Existing literature reveals a critical gap: theoretical algorithms in software ignore strict
substation line-rate execution constraints, while existing hardware prototypes often rely on
simplistic univariate thresholding that remains vulnerable to coordinated stealth attacks ($\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$).
Furthermore, prior studies frequently neglect fixed-point quantization dynamics and evaluate only a
single attack profile. A clear requirement exists for a hardware-efficient, dual-layer statistical
anomaly engine coupling spatial Mahalanobis distance with temporal two-sided CUSUM on FPGA, verified
across multiple adversarial attack regimes with rigorous fixed-point safeguards.

\section{Chapter Summary}
This chapter reviewed smart-grid architecture, the mathematical stealth FDI condition, and the
failure of conventional bad-data detection. The complementary properties of spatial Mahalanobis
distance and temporal two-sided CUSUM were analyzed, and FPGA fixed-point implementation considerations
were detailed. A comparative analysis and research gap established the foundation for the proposed
dual-layer hardware architecture, formulated mathematically in Chapter Three.
"""

print("Concise Chapter 2 module loaded.")
