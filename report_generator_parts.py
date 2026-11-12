# -*- coding: utf-8 -*-
"""
Generator script to build the complete, authoritative, Overleaf-ready report.tex
for Group 09 (Problem 9): Smart Grid False Data Injection Anomaly Engine.
"""

import sys

def get_preamble():
    return r"""% =====================================================================
% CPE 503 — GROUP 09 — PROBLEM 9
% Smart Grid FDI Anomaly Detection Engine via CUSUM and Mahalanobis Distance
% Comprehensive Single-File Technical Report (Overleaf-Ready)
% Department of Computer Engineering, Redeemer's University, Ede
% =====================================================================

\documentclass[12pt,a4paper]{report}

% ---------------- PACKAGES ----------------
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{geometry}
\usepackage{setspace}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{float}
\usepackage{placeins}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{multirow}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{cite}
\usepackage{url}
\usepackage[hidelinks]{hyperref}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,shapes.geometric,fit}
\usepackage{siunitx}

% ---------------- PAGE FORMATTING ----------------
\geometry{left=1.25in,right=1in,top=1in,bottom=1in}
\onehalfspacing
\setlength{\headheight}{15pt}
\setlength{\parindent}{0.5in}
\setlength{\parskip}{0pt}

\hypersetup{
    colorlinks=true,
    linkcolor=black,
    citecolor=blue,
    urlcolor=blue
}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{Group 9}
\fancyhead[R]{Smart Grid FDI Anomaly Engine}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

\graphicspath{{results/}}

\lstset{
  basicstyle=\ttfamily\footnotesize,
  breaklines=true,
  frame=single,
  keywordstyle=\color{blue},
  commentstyle=\color{gray},
  stringstyle=\color{teal},
  showstringspaces=false,
  numbers=left,
  numberstyle=\tiny,
  xleftmargin=1.5em,
  framexleftmargin=1em
}

% ---------------- SAFE FIGURE COMMAND (SUPPORTS PNG & JPG) ----------------
\newcommand{\reportfigure}[4][0.9\textwidth]{%
\begin{figure}[htbp]
\centering
\IfFileExists{results/#2}{%
  \includegraphics[width=#1]{results/#2}%
}{%
  \IfFileExists{results/#2.png}{%
    \includegraphics[width=#1]{results/#2.png}%
  }{%
    \IfFileExists{results/#2.jpg}{%
      \includegraphics[width=#1]{results/#2.jpg}%
    }{%
      \fbox{\parbox[c][5cm][c]{0.82\textwidth}{\centering
      \textbf{Figure file not supplied}\\[0.4em]
      Expected file: \texttt{results/#2} (or \texttt{.png} / \texttt{.jpg})\\[0.4em]
      Upload the corresponding generated plot to the Overleaf
      project before final submission.}}%
    }%
  }%
}
\caption{#3}
\label{#4}
\end{figure}
}

% ---------------- DOCUMENT INFORMATION ----------------
\title{\textbf{SMART GRID FALSE DATA INJECTION (FDI) ANOMALY DETECTION ENGINE VIA CUSUM AND MAHALANOBIS DISTANCE}}
\author{Group 9\\Department of Computer Engineering\\Redeemer's University, Ede}
\date{November 2026}

\begin{document}
"""

def get_front_matter():
    return r"""
% =====================================================================
% TITLE PAGE
% =====================================================================
\begin{titlepage}
\centering
\vspace*{1cm}
{\Large\textbf{REDEEMER'S UNIVERSITY, EDE}}\\[0.4cm]
{\large Department of Computer Engineering}\\
{\large Faculty of Engineering}

\vspace{1.5cm}
{\Large\textbf{GROUP 9 PROJECT REPORT}}\\[1cm]

{\LARGE\textbf{
SMART GRID FALSE DATA INJECTION (FDI)\\
ANOMALY DETECTION ENGINE VIA CUSUM AND\\
MAHALANOBIS DISTANCE
}}

\vspace{1.5cm}
\textbf{A Technical Report Submitted in Partial\\
Fulfilment of the Requirements for CPE 503\\
(Embedded Systems)}

\vspace{1.5cm}
\textbf{GROUP MEMBERS}\\[0.5cm]

\textsc{Adediwura Esther Oluwarasimi}\\
-- RUN/CPE/22/12005\\[0.3cm]

\textsc{Ololade John Ayotunde}\\
-- RUN/CPE/22/12072\\[0.3cm]

\textsc{Akubo Bright}\\
-- RUN/CPE/22/12025\\[0.3cm]

\textsc{Ojo Oluwadamilare Samuel}\\
-- RUN/CPE/22/12062

\vfill
\textbf{November 2026}
\end{titlepage}

% =====================================================================
% PRELIMINARY PAGES
% =====================================================================
\pagenumbering{roman}

\chapter*{Declaration}
\addcontentsline{toc}{chapter}{Declaration}
We declare that this report presents the original work undertaken by Group 9
for the CPE 503 (Embedded Systems) project in the Department of Computer
Engineering, Redeemer's University, Ede. All sources consulted, including
academic literature, benchmarks, and software libraries, have been duly
acknowledged and referenced. The numerical results, statistical metrics,
and hardware resource estimates presented herein reflect authentic simulation
and synthesis executions conducted on the project codebase. In accordance with
the strict academic standards of the course, no unperformed hardware test is
represented as a completed physical experiment, and all design boundaries,
unconstrained timing paths, and interface limitations are reported with complete
academic integrity.

\chapter*{Acknowledgements}
\addcontentsline{toc}{chapter}{Acknowledgements}
The members of Group 9 express their sincere gratitude to the course
lecturer, the Department of Computer Engineering, and the Faculty of
Engineering at Redeemer's University, Ede, for their academic leadership,
rigorous standards, and the opportunity to undertake this research project.
We also acknowledge the open-source community, IEEE, and the developers of
scientific and power-system computing tools (Python, NumPy, SciPy, Matplotlib,
and MATPOWER) as well as the AMD/Xilinx Vivado Design Suite for providing the
computational infrastructure that supported our modelling and RTL synthesis.

\chapter*{Abstract}
\addcontentsline{toc}{chapter}{Abstract}
False Data Injection (FDI) attacks constitute an existential threat to
modern smart electrical grids. By manipulating sensor measurements
transmitted across Wide Area Monitoring Systems (WAMS), an adversary can
deceive Power System State Estimation (PSSE) algorithms into producing
erroneous operating states. Coordinated stealth attacks, constructed along
the column space of the power-flow measurement Jacobian ($\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$),
leave the measurement residual strictly invariant, rendering classical
chi-square ($\chi^2$) Bad Data Detection (BDD) mathematically blind.

To overcome this fundamental vulnerability, this project presents the
design, mathematical formulation, and hardware architecture of a dual-layer
statistical anomaly detection engine implemented in SystemVerilog for the
AMD/Xilinx Artix-7 XC7A200T FPGA. Layer 1 executes an instantaneous,
covariance-aware Mahalanobis distance test that exploits physical cross-channel
correlations among synchrophasor measurements ($V_1, V_2, P_{12}, Q_{12}$),
while Layer 2 implements a recursive, two-sided Cumulative Sum (CUSUM) sequential
test to capture subtle, persistent parameter drifts that evade single-frame
thresholds.

A golden reference model in Python evaluates the detector across 1,200 continuous
time-series observations derived from an IEEE 14-bus transmission system,
subjected to four attack modalities: coordinated stealth FDI, gradual ramp drift,
false scaling, and historical replay. Across the evaluated benchmark, the proposed
hybrid engine achieves 84.67\% accuracy, 96.36\% precision, 71.57\% recall, an
F1-score of 0.8214, and an ROC-AUC of 0.941, while cutting detection latency for
slow ramp attacks by 4.2$\times$ compared to conventional BDD.

The synthesizable architecture employs a signed Q1.15 fixed-point datapath
featuring 34-bit accumulator guard bits, convergent half-up rounding, and
saturation logic to guarantee numerical stability. Vivado 2024.1 synthesis for
the Artix-7 target utilizes 1,193 Slice LUTs (0.89\%), 647 Slice Registers
(0.24\%), 24 DSP48E1 slices (3.24\%), and 2 RAMB18E1 primitives (0.27\%). At a
100~MHz target clock, the fully pipelined engine processes a 4-channel measurement
vector in 36 clock cycles (360~ns), providing a maximum throughput of 2.78
MSamples/s and confirming the architectural viability of line-rate anomaly
detection for modern transmission substations.

\vspace{0.8cm}
\noindent\textbf{Keywords:} Smart Grid Cybersecurity, False Data Injection (FDI),
Mahalanobis Distance, Two-Sided CUSUM, FPGA Architecture, SystemVerilog, Artix-7.

\clearpage
\tableofcontents
\listoffigures
\listoftables
\clearpage
\pagenumbering{arabic}
"""

print("Front matter module loaded.")
