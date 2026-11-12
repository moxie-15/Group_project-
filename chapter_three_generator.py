# -*- coding: utf-8 -*-
"""
Chapter 3 generator for CPE 503 Group 09 report.
Contains formal mathematical derivations, state estimation models, stealth proof,
Table 3.1 (Notation and Symbols - Lecturer Table 1), and Table 3.2 (Fixed-Point Q1.15
Design Parameters - Lecturer Table 6).
"""

def get_chapter_three():
    return r"""
% =====================================================================
% CHAPTER THREE
% =====================================================================
\chapter{Mathematical Formulation and Fixed-Point Design}

\section{System Model and Mathematical Notation}
Power system monitoring relies on continuous acquisition of synchronized telemetry
representing the physical operating state of the electrical transmission network.
To establish mathematical rigor across both algorithmic formulation and digital
hardware implementation, Table~\ref{tab:notation} defines the principal symbols,
their physical meanings, coordinate formats, and operational units utilized
throughout this report.

\begin{table}[H]
\centering
\caption{Notation and mathematical symbols used throughout the report.}
\label{tab:notation}
\small
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{|p{2.2cm}|p{7.2cm}|p{2.6cm}|p{2.2cm}|}
\hline
\textbf{Symbol} & \textbf{Mathematical Definition / Physical Meaning} & \textbf{Data Format} & \textbf{Physical Unit} \\
\hline
$y_t$ & Scalar monitored measurement or observation at time $t$ & Signed Q1.15 & p.u. (normalized) \\
\hline
$D_t^2$ & Squared Mahalanobis distance statistic at time $t$ & Signed Q1.15 & Dimensionless \\
\hline
$S_t$ & Cumulative Sum (CUSUM) statistic at time $t$ & Signed Q1.15 & Dimensionless \\
\hline
$h$ & CUSUM decision alarm threshold & Signed Q1.15 & Dimensionless \\
\hline
$k$ & CUSUM reference allowance / slack parameter ($k = \delta/2$) & Signed Q1.15 & Dimensionless \\
\hline
$\boldsymbol{\Sigma}$ & Feature covariance matrix ($d \times d$) & Double / Q1.15 & $\text{p.u.}^2$ \\
\hline
$\boldsymbol{\Sigma}^{-1}, \boldsymbol{W}$ & Inverse covariance (precision) matrix & Signed Q1.15 & $\text{p.u.}^{-2}$ \\
\hline
$\boldsymbol{r}_t$ & Power system state-estimation measurement residual & Real vector & Physical / p.u. \\
\hline
$\alpha$ & False-alarm probability / significance level & Scalar & Probability \\
\hline
$\boldsymbol{z}_t$ & Raw power-system PMU measurement vector ($m \times 1$) & Vector & kV, A, MW, MVAR \\
\hline
$\boldsymbol{x}_t$ & True power-system complex state vector ($n \times 1$) & Vector & Radian, p.u. \\
\hline
$\hat{\boldsymbol{x}}_t$ & Weighted Least-Squares estimated system state & Vector & Radian, p.u. \\
\hline
$\boldsymbol{H}$ & Power system measurement Jacobian / topology matrix & Matrix & Model-dependent \\
\hline
$\boldsymbol{a}_t$ & False Data Injection perturbation vector ($\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$) & Vector & Physical / p.u. \\
\hline
$\boldsymbol{c}$ & Attacker false state bias vector & Vector & Radian, p.u. \\
\hline
$\boldsymbol{\mu}$ & Nominal reference feature mean vector ($d \times 1$) & Signed Q1.15 & p.u. (normalized) \\
\hline
$\boldsymbol{q}_t$ & Preprocessed, mean-centered 4-channel feature vector & Signed Q1.15 & p.u. (normalized) \\
\hline
$\tau^2$ & Spatial Mahalanobis decision threshold ($\chi^2_{d, 1-\alpha}$) & Signed Q1.15 & Dimensionless \\
\hline
$S_t^+, S_t^-$ & Two-sided positive and negative recursive CUSUM accumulators & Signed Q1.15 & Dimensionless \\
\hline
$\text{ARL}_0$ & In-control Average Run Length (mean time between false alarms)& Integer & Sample frames \\
\hline
$\text{ARL}_1$ & Out-of-control Average Run Length (mean detection delay) & Integer & Sample frames \\
\hline
\end{tabular}
\end{table}

\section{False Data Injection Model and the Stealth Condition}
The transmission grid telemetry acquisition process is formulated under the linear DC
power-flow approximation or linearized AC operating point:
\begin{equation}
\boldsymbol{z} = \boldsymbol{H}\boldsymbol{x} + \boldsymbol{e},
\label{eq:ch3_dc_model}
\end{equation}
where $\boldsymbol{z} \in \mathbb{R}^m$ is the vector of $m$ measurements, $\boldsymbol{x} \in \mathbb{R}^n$
is the state vector of $n$ bus voltage angles (with $m > n$ to ensure system observability),
and $\boldsymbol{e} \sim \mathcal{N}(\boldsymbol{0}, \boldsymbol{R})$ represents independent,
zero-mean Gaussian measurement errors with known diagonal covariance matrix
$\boldsymbol{R} = \text{diag}(\sigma_1^2, \dots, \sigma_m^2)$.

An adversary executing a False Data Injection (FDI) attack introduces an additive
perturbation vector $\boldsymbol{a} \in \mathbb{R}^m$ into the telemetry stream:
\begin{equation}
\boldsymbol{z}_a = \boldsymbol{z} + \boldsymbol{a}.
\label{eq:ch3_attack_stream}
\end{equation}
The attack is defined as \textbf{coordinated stealth FDI} if the adversary constructs
$\boldsymbol{a}$ as a linear combination of the columns of the measurement matrix $\boldsymbol{H}$:
\begin{equation}
\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}, \quad \text{for some non-zero } \boldsymbol{c} \in \mathbb{R}^n,
\label{eq:ch3_stealth_definition}
\end{equation}
where $\boldsymbol{c}$ denotes an arbitrary false state bias vector deliberately injected
into the power system operating state.

\section{Weighted Least-Squares State Estimation and Residual Invariance}
The Weighted Least-Squares (WLS) state estimator computes the state estimate $\hat{\boldsymbol{x}}$
that minimizes the weighted sum of squared residuals:
\begin{equation}
J(\boldsymbol{x}) = [\boldsymbol{z} - \boldsymbol{H}\boldsymbol{x}]^T \boldsymbol{R}^{-1} [\boldsymbol{z} - \boldsymbol{H}\boldsymbol{x}].
\label{eq:ch3_wls_cost}
\end{equation}
Differentiating Equation~\eqref{eq:ch3_wls_cost} with respect to $\boldsymbol{x}$ and equating
to zero yields the normal equations:
\begin{equation}
\boldsymbol{H}^T \boldsymbol{R}^{-1} [\boldsymbol{z} - \boldsymbol{H}\hat{\boldsymbol{x}}] = \boldsymbol{0} \implies \hat{\boldsymbol{x}} = (\boldsymbol{H}^T \boldsymbol{R}^{-1} \boldsymbol{H})^{-1} \boldsymbol{H}^T \boldsymbol{R}^{-1} \boldsymbol{z}.
\label{eq:ch3_normal_eqs}
\end{equation}
Let $\boldsymbol{G} = \boldsymbol{H}^T \boldsymbol{R}^{-1} \boldsymbol{H}$ denote the symmetric,
positive-definite power-system gain matrix. The state estimation projection is $\hat{\boldsymbol{x}} = \boldsymbol{G}^{-1} \boldsymbol{H}^T \boldsymbol{R}^{-1} \boldsymbol{z}$.

Under nominal clean operation, the measurement residual vector is:
\begin{equation}
\boldsymbol{r} = \boldsymbol{z} - \boldsymbol{H}\hat{\boldsymbol{x}} = [\boldsymbol{I} - \boldsymbol{H}\boldsymbol{G}^{-1}\boldsymbol{H}^T\boldsymbol{R}^{-1}]\boldsymbol{z} = (\boldsymbol{I} - \boldsymbol{K})\boldsymbol{z},
\label{eq:ch3_clean_residual}
\end{equation}
where $\boldsymbol{K} = \boldsymbol{H}\boldsymbol{G}^{-1}\boldsymbol{H}^T\boldsymbol{R}^{-1}$ is the
orthogonal projection (hat) matrix.

\begin{quote}
\textbf{Theorem 1 (Residual Invariance under Stealth FDI):}
\textit{Let $\boldsymbol{z}_a = \boldsymbol{z} + \boldsymbol{H}\boldsymbol{c}$ represent an attacked
measurement vector. The post-attack state estimate is $\hat{\boldsymbol{x}}_a = \hat{\boldsymbol{x}} + \boldsymbol{c}$,
and the resulting post-attack residual $\boldsymbol{r}_a$ is strictly identical to the pre-attack residual $\boldsymbol{r}$.}
\end{quote}

\noindent\textbf{Proof:}
Applying the linear WLS estimator to the corrupted vector $\boldsymbol{z}_a$:
\begin{align}
\hat{\boldsymbol{x}}_a &= \boldsymbol{G}^{-1} \boldsymbol{H}^T \boldsymbol{R}^{-1} \boldsymbol{z}_a \nonumber \\
&= \boldsymbol{G}^{-1} \boldsymbol{H}^T \boldsymbol{R}^{-1} (\boldsymbol{z} + \boldsymbol{H}\boldsymbol{c}) \nonumber \\
&= \boldsymbol{G}^{-1} \boldsymbol{H}^T \boldsymbol{R}^{-1} \boldsymbol{z} + \boldsymbol{G}^{-1} (\boldsymbol{H}^T \boldsymbol{R}^{-1} \boldsymbol{H})\boldsymbol{c} \nonumber \\
&= \hat{\boldsymbol{x}} + \boldsymbol{G}^{-1}\boldsymbol{G}\boldsymbol{c} \nonumber \\
&= \hat{\boldsymbol{x}} + \boldsymbol{c}.
\end{align}
Evaluating the post-attack measurement residual:
\begin{align}
\boldsymbol{r}_a &= \boldsymbol{z}_a - \boldsymbol{H}\hat{\boldsymbol{x}}_a \nonumber \\
&= (\boldsymbol{z} + \boldsymbol{H}\boldsymbol{c}) - \boldsymbol{H}(\hat{\boldsymbol{x}} + \boldsymbol{c}) \nonumber \\
&= \boldsymbol{z} + \boldsymbol{H}\boldsymbol{c} - \boldsymbol{H}\hat{\boldsymbol{x}} - \boldsymbol{H}\boldsymbol{c} \nonumber \\
&= \boldsymbol{z} - \boldsymbol{H}\hat{\boldsymbol{x}} \nonumber \\
&= \boldsymbol{r}.
\end{align}
Evaluating the global chi-square detection statistic:
\begin{equation}
J(\hat{\boldsymbol{x}}_a) = \boldsymbol{r}_a^T \boldsymbol{R}^{-1} \boldsymbol{r}_a = \boldsymbol{r}^T \boldsymbol{R}^{-1} \boldsymbol{r} = J(\hat{\boldsymbol{x}}).
\end{equation}
Thus, $J(\hat{\boldsymbol{x}}_a)$ is mathematically identical to $J(\hat{\boldsymbol{x}})$. The
chi-square test fails to detect the attack, completing the proof. \hfill $\blacksquare$

\section{Spatial Mahalanobis-Distance Detector Formulation}
Because the state-estimation residual is invariant under $\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$,
detection must exploit the multivariate statistical relationships governing local physical
quantities. Let $\boldsymbol{q}_t \in \mathbb{R}^d$ ($d=4$) represent the localized synchrophasor
feature vector capturing terminal bus voltages and active/reactive branch flows ($V_1, V_2, P_{12}, Q_{12}$)
at sampling instant $t$.

During a clean, unattacked baseline calibration period $t \in [1, T_{\text{cal}}]$, the nominal
feature mean vector $\boldsymbol{\mu} \in \mathbb{R}^d$ and sample covariance matrix
$\boldsymbol{\Sigma} \in \mathbb{R}^{d \times d}$ are computed:
\begin{align}
\boldsymbol{\mu} &= \frac{1}{T_{\text{cal}}} \sum_{t=1}^{T_{\text{cal}}} \boldsymbol{q}_t, \label{eq:ch3_mean_est} \\
\boldsymbol{\Sigma} &= \frac{1}{T_{\text{cal}} - 1} \sum_{t=1}^{T_{\text{cal}}} (\boldsymbol{q}_t - \boldsymbol{\mu})(\boldsymbol{q}_t - \boldsymbol{\mu})^T. \label{eq:ch3_cov_est}
\end{align}
To eliminate the requirement for online matrix inversion inside the hardware datapath, the
precision matrix $\boldsymbol{W} = \boldsymbol{\Sigma}^{-1}$ is precomputed offline and loaded
into static FPGA configuration registers.

For each incoming observation $\boldsymbol{q}_t$, the preprocessed deviation vector is
$\Delta\boldsymbol{q}_t = \boldsymbol{q}_t - \boldsymbol{\mu}$. The instantaneous squared
Mahalanobis distance statistic is:
\begin{equation}
D_t^2 = \Delta\boldsymbol{q}_t^T \boldsymbol{W} \Delta\boldsymbol{q}_t = \sum_{i=1}^d \sum_{j=1}^d \Delta q_{t,i} W_{ij} \Delta q_{t,j}.
\label{eq:ch3_mahal_stat}
\end{equation}
Under the null hypothesis of uncorrupted, stationary Gaussian operation ($H_0: \boldsymbol{q}_t \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$),
the quadratic statistic $D_t^2$ is distributed as a central chi-square random variable with
$d = 4$ degrees of freedom:
\begin{equation}
D_t^2 \sim \chi^2_d.
\end{equation}
The Layer 1 spatial decision rule asserts an alarm flag $A_{M,t}$ whenever $D_t^2$ exceeds
the calibrated threshold $\tau^2$:
\begin{equation}
A_{M,t} = \begin{cases}
1, & \text{if } D_t^2 > \tau^2, \\
0, & \text{if } D_t^2 \le \tau^2,
\end{cases}
\quad \text{where } \Pr(D_t^2 > \tau^2 \mid H_0) = \alpha.
\label{eq:ch3_layer1_decision}
\end{equation}

\section{Temporal Two-Sided CUSUM Sequential Detector Formulation}
While Layer 1 provides single-cycle detection for abrupt and scaling attacks, slow ramp
attacks with small injection rates ($\boldsymbol{a}_t = \beta t \boldsymbol{H}\boldsymbol{c}$)
produce instantaneous deviations that remain below $\tau^2$ during initial phases.
Layer 2 addresses this vulnerability by deploying a recursive, two-sided Cumulative Sum
(CUSUM) filter to integrate subtle persistent shifts over time.

Let $y_{c,t}$ denote the normalized scalar telemetry signal for channel $c \in \{1, \dots, d\}$
at time $t$, with nominal reference mean $\nu_{0,c}$. The two-sided recursive CUSUM
formulation tracks positive shifts ($S_{c,t}^+$) and negative shifts ($S_{c,t}^-$):
\begin{align}
S_{c,t}^+ &= \max\left(0, \; S_{c,t-1}^+ + (y_{c,t} - \nu_{0,c}) - k_c\right), \label{eq:ch3_cusum_pos} \\
S_{c,t}^- &= \max\left(0, \; S_{c,t-1}^- - (y_{c,t} - \nu_{0,c}) - k_c\right), \label{eq:ch3_cusum_neg}
\end{align}
with initial boundary conditions $S_{c,0}^+ = S_{c,0}^- = 0$.

The CUSUM parameters are mathematically derived from the target shift magnitude $\delta_c$:
\begin{equation}
k_c = \frac{\delta_c}{2},
\end{equation}
which establishes the drift allowance deadband. The alarm threshold $h_c$ is determined
to balance the in-control run length $\text{ARL}_0$ against out-of-control detection delay $\text{ARL}_1$.

The Layer 2 temporal decision rule asserts an alarm flag $A_{C,c,t}$ for channel $c$ if
either accumulator crosses threshold $h_c$:
\begin{equation}
A_{C,c,t} = \begin{cases}
1, & \text{if } S_{c,t}^+ > h_c \quad \text{or} \quad S_{c,t}^- > h_c, \\
0, & \text{otherwise}.
\end{cases}
\label{eq:ch3_layer2_decision}
\end{equation}

\section{Combined Dual-Layer Decision Rule}
The global anomaly decision flag $A_t \in \{0, 1\}$ at time step $t$ is formulated as the
logical disjunction (OR) of the spatial Mahalanobis alert and all multi-channel temporal
CUSUM alerts:
\begin{equation}
A_t = A_{M,t} \lor \left( \bigvee_{c=1}^d A_{C,c,t} \right).
\label{eq:ch3_global_decision}
\end{equation}
This synergistic formulation guarantees that an alarm is declared immediately if an abrupt
structural perturbation violates spatial cross-channel covariance ($A_{M,t} = 1$) or if a
subtle gradual drift accumulates sufficient temporal evidence to trip CUSUM ($A_{C,c,t} = 1$).

\section{Feature Normalization and Mean-Centering}
Power system telemetry variables encompass vastly different physical units and magnitudes:
voltage magnitudes hover near $1.0~\text{p.u.}$ ($13.8\text{--}138~\text{kV}$), while branch
active power flows can span hundreds of megawatts. In digital fixed-point hardware, raw
unscaled numbers would cause catastrophic dynamic range underflow in fractional channels
and severe overflow in high-power channels.

To establish uniform numerical conditioning, each raw measurement $z_c$ is linearly mapped
into a normalized fixed-point range using nominal baseline operating points:
\begin{equation}
q_c = \frac{z_c - \bar{z}_c}{\sigma_{z,c}} \times \text{ScaleFactor},
\end{equation}
ensuring that all preprocessed features $\Delta q_c = q_c - \mu_c$ conform strictly to the
$[-1.0, +0.999969]$ boundaries of the signed Q1.15 numerical format.

\section{Fixed-Point Signed Q1.15 Arithmetic and Quantization Error Analysis}
Digital signal processing algorithms targeting FPGA fabric face a fundamental trade-off
between numerical precision and silicon resource utilization. Floating-point arithmetic
incurs high DSP slice consumption and multi-cycle pipeline latency. This project implements
a uniform signed \textbf{Q1.15} fixed-point representation for all inputs, calibration
matrices, and arithmetic datapaths.

A 16-bit signed two's-complement word in Q1.15 format consists of 1 sign bit and 15 fractional
bits. Its decimal value is:
\begin{equation}
X = -b_{15} + \sum_{i=0}^{14} b_i 2^{i - 15}, \quad b_i \in \{0, 1\}.
\end{equation}
The quantization step size is $\Delta = 2^{-15} \approx 3.051758 \times 10^{-5}$. Assuming
round-off quantization noise $e_q$ is uniformly distributed over $[-\Delta/2, +\Delta/2]$,
the noise variance is:
\begin{equation}
\sigma_q^2 = \frac{\Delta^2}{12} = \frac{2^{-30}}{12} \approx 7.761 \times 10^{-11}.
\end{equation}
The Signal-to-Quantization-Noise Ratio (SQNR) for a full-scale sinusoidal input is:
\begin{equation}
\text{SQNR} = 6.0206 \times 15 + 1.7609 \approx 92.07~\text{dB}.
\end{equation}
This theoretical noise floor is over $25~\text{dB}$ below the typical $0.1\%$ total vector
error (TVE) threshold mandated by the IEEE~C37.118 synchrophasor standard, proving that Q1.15
fixed-point representation introduces negligible distortion into the anomaly detection process.

\section{Accumulator Word Length, Guard Bits, and Saturation Safeguards}
When evaluating the matrix-vector multiplication $\boldsymbol{y} = \boldsymbol{W} \Delta\boldsymbol{q}$
and the subsequent quadratic dot product $D^2 = \Delta\boldsymbol{q}^T \boldsymbol{y}$, two 16-bit
Q1.15 operands are multiplied, generating an exact 32-bit product:
\begin{equation}
\text{Q1.15} \times \text{Q1.15} \implies \text{Q2.30 (32 bits)}.
\end{equation}
The dot product computes the sum of $d = 4$ products. In the worst-case scenario where all
terms attain full-scale values simultaneously, intermediate summation can cause bit overflow.
To mathematically eliminate overflow, the accumulator word length must include guard bits:
\begin{equation}
N_{\text{guard}} = \lceil \log_2(d) \rceil = \lceil \log_2(4) \rceil = 2~\text{bits}.
\end{equation}
Thus, the internal accumulation register is sized to \textbf{34 bits (Q4.30)}, providing
dynamic range $[-4.0, +3.9999999]$ with 30 fractional bits.

Following accumulation, the 34-bit value is scaled back to 16 bits using convergent half-up
rounding by adding $+2^{14} = \text{0x0000\_4000}$ before truncating bits $[30:15]$. To protect
against two's-complement arithmetic overflow (e.g., $-1.0 \times -1.0 = +1.0$, which exceeds
the maximum positive Q1.15 representable value of $+0.999969$), dedicated saturation logic
clamps any overflow to `0x7FFF` (+0.999969) and any underflow to `0x8000` (-1.0).

\section{Project Calibration Parameters and Fixed-Point Wordlengths}
Table~\ref{tab:q15_params} summarizes the complete fixed-point parameter configuration,
word lengths, quantization boundaries, and architectural assignments implemented in the
RTL design.

\begin{table}[H]
\centering
\caption{Fixed-point Q1.15 design parameters and quantization boundaries.}
\label{tab:q15_params}
\small
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{|p{2.6cm}|p{4.2cm}|p{2.0cm}|p{1.4cm}|p{2.4cm}|p{2.4cm}|}
\hline
\textbf{Parameter} & \textbf{Physical Description} & \textbf{Format} & \textbf{Bits} & \textbf{Scaling ($2^{-15}$)} & \textbf{Dynamic Range} \\
\hline
$z_c$ & PMU input telemetry vector & Signed Q1.15 & 16 & $3.0518 \times 10^{-5}$ & $[-1.0, +0.99997]$ \\
\hline
$\mu_c$ & Historical baseline mean vector & Signed Q1.15 & 16 & $3.0518 \times 10^{-5}$ & $[-1.0, +0.99997]$ \\
\hline
$r_c = z_c - \mu_c$ & Preprocessed deviation residual & Signed Q1.15 & 16 & $3.0518 \times 10^{-5}$ & $[-1.0, +0.99997]$ \\
\hline
$W_{ij}$ & Inverse covariance matrix entry & Signed Q1.15 & 16 & $3.0518 \times 10^{-5}$ & $[-1.0, +0.99997]$ \\
\hline
$P_{\text{mult}}$ & DSP multiplier product & Signed Q2.30 & 32 & $9.3132 \times 10^{-10}$ & $[-2.0, +1.99999]$ \\
\hline
$A_{\text{dot}}$ & Dot-product accumulator & Signed Q4.30 & 34 & $9.3132 \times 10^{-10}$ & $[-8.0, +7.99999]$ \\
\hline
$D^2$ & Squared Mahalanobis distance & Signed Q1.15 & 16 & $3.0518 \times 10^{-5}$ & $[0.0, +0.99997]$ \\
\hline
$\tau^2$ & Spatial decision threshold & Signed Q1.15 & 16 & $1673 \times 2^{-15}$ & $0.05106~\text{p.u.}$ \\
\hline
$k$ & CUSUM reference slack allowance & Signed Q1.15 & 16 & $5461 \times 2^{-15}$ & $0.16667~\text{p.u.}$ \\
\hline
$h$ & CUSUM decision alarm threshold & Signed Q1.15 & 16 & $20753 \times 2^{-15}$ & $0.63333~\text{p.u.}$ \\
\hline
\end{tabular}
\end{table}

\section{Hardware Latency and Throughput Closed-Form Mathematical Model}
To provide analytical performance guarantees prior to hardware synthesis, closed-form
equations model execution latency, processing throughput, and power dissipation.

Let $f_{\text{clk}}$ denote the system clock frequency and $T_{\text{clk}} = 1/f_{\text{clk}}$
denote the clock period. The total execution latency $T_{\text{latency}}$ to process a single
4-channel measurement frame through the FSM controller and pipelined datapath is:
\begin{equation}
T_{\text{latency}} = \frac{N_{\text{cycles}}}{f_{\text{clk}}},
\label{eq:ch3_latency_model}
\end{equation}
where $N_{\text{cycles}}$ is the cycle count derived from the state machine schedule.
For the 4-channel engine operating at $f_{\text{clk}} = 100~\text{MHz}$ ($T_{\text{clk}} = 10~\text{ns}$)
with $N_{\text{cycles}} = 36$~cycles:
\begin{equation}
T_{\text{latency}} = 36 \times 10~\text{ns} = 360~\text{ns} = 0.36~\mu\text{s}.
\end{equation}

The theoretical maximum processing throughput in measurement frames per second is:
\begin{equation}
\text{Throughput} = \frac{f_{\text{clk}}}{N_{\text{cycles}}} = \frac{100 \times 10^6}{36} \approx 2,777,777~\text{frames/s} \approx 2.78~\text{MSamples/s}.
\label{eq:ch3_throughput_model}
\end{equation}

The maximum attainable operating clock frequency $f_{\max}$ is bounded by the critical
path delay $T_{\text{crit}}$ and Worst Negative Slack (WNS):
\begin{equation}
f_{\max} = \frac{1}{T_{\text{clk}} - \text{WNS}}.
\label{eq:ch3_fmax_model}
\end{equation}

The dynamic energy consumed per anomaly detection operation $E_{\text{op}}$ is given by:
\begin{equation}
E_{\text{op}} = P_{\text{dyn}} \times T_{\text{latency}} = P_{\text{dyn}} \times \left( \frac{N_{\text{cycles}}}{f_{\text{clk}}} \right),
\label{eq:ch3_energy_model}
\end{equation}
where $P_{\text{dyn}}$ is the dynamic power reported by Vivado power analysis. These analytical
models are verified experimentally against Vivado synthesis reports in Chapter Five.
"""

print("Chapter 3 module loaded.")
