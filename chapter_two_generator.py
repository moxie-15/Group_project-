# -*- coding: utf-8 -*-
"""
Chapter 2 generator for CPE 503 Group 09 report.
Adheres strictly to the user's requested 14-section sequence, integrates the user's
exact text for Sections 2.1 and 2.2 (including Table 2.1), and presents Table 2.2
(Table 2 of the lecturer's requirements) with full peer-reviewed citations.
"""

def get_chapter_two():
    return r"""
% =====================================================================
% CHAPTER TWO
% =====================================================================
\chapter{Literature Review}

\section{Introduction}
The increasing integration of information and communication technologies into modern
electrical power systems has transformed the traditional electricity grid into a more
interconnected, automated, and data-driven infrastructure commonly referred to as the
smart grid. Unlike conventional power networks, which rely heavily on relatively isolated
monitoring and control mechanisms, smart grids incorporate advanced metering infrastructure,
intelligent electronic devices, phasor measurement units (PMUs), supervisory control and
data acquisition (SCADA) systems, communication networks, and automated control platforms.
These technologies facilitate continuous monitoring of power system conditions, improve
operational efficiency, support real-time decision-making, and enhance the reliability of
electricity supply. However, the increased dependence on digital communication and
interconnected control systems also introduces cybersecurity vulnerabilities that may be
exploited by malicious actors.

One significant cybersecurity threat to smart-grid infrastructure is the False Data
Injection (FDI) attack. This type of attack involves the deliberate manipulation of
measurement data transmitted to a power system monitoring or state estimation unit.
By introducing carefully constructed false measurements, an attacker may influence the
estimated operating condition of the network without necessarily producing obvious
abnormalities in the measurement data. Such manipulation can potentially affect operational
decisions, compromise situational awareness, and interfere with the reliable operation
of the electrical power system. The ability of certain FDI attacks to bypass conventional
bad-data detection techniques makes their identification an important research problem
in smart-grid cybersecurity.

Several approaches have been investigated for detecting abnormal measurements and malicious
data manipulation in power systems. Traditional bad-data detection techniques commonly
rely on statistical residual analysis, measurement consistency checks, and threshold-based
decision rules. Although these methods provide useful mechanisms for identifying measurement
errors and certain forms of data manipulation, their effectiveness may be limited when an
attacker exploits the mathematical structure of the state estimation process. Consequently,
researchers have explored alternative detection techniques capable of examining the
statistical characteristics of measurements and identifying deviations that may not be
immediately apparent through conventional residual-based methods.

Multivariate statistical techniques provide one possible approach to this problem because
measurements obtained from a power system are often correlated. Rather than examining each
measurement independently, multivariate methods consider the relationships among multiple
variables when determining whether an observation is consistent with expected system behaviour.
One widely recognised technique is the Mahalanobis distance, which measures the distance
between an observation and a reference distribution while accounting for the covariance
structure of the data. This property makes it useful for identifying observations that
deviate from normal operating patterns, particularly when the variables involved have different
scales or exhibit statistical correlations. Nevertheless, the performance of Mahalanobis-distance-based
detection depends on the quality of the reference data, covariance estimation, threshold
selection, and the characteristics of the abnormal behaviour being investigated.

Another important approach to anomaly detection is sequential change detection. Unlike methods
that evaluate observations independently, sequential techniques analyse the evolution of a
detection statistic over time. The Cumulative Sum (CUSUM) algorithm is a well-established
statistical process monitoring technique that accumulates evidence of deviations from an
expected reference condition. By maintaining a cumulative statistic and comparing it against
a predefined decision threshold, CUSUM can identify persistent changes that may not produce
sufficiently large deviations in individual samples. Its relatively simple recursive structure
makes it attractive for applications where continuous monitoring, predictable computational
requirements, and timely detection are important.

The combination of multivariate statistical analysis and sequential change detection presents
an opportunity to develop a detector that considers both the statistical characteristics of
measurement data and the persistence of abnormal behaviour over time. In this study, Mahalanobis
distance and CUSUM are considered as complementary detection mechanisms within a smart-grid
False Data Injection anomaly detection architecture. The Mahalanobis distance provides a
measure of deviation from a reference statistical distribution, while CUSUM evaluates the
accumulation of evidence across successive observations. The effectiveness of this combination,
however, depends on the mathematical formulation, calibration procedure, decision thresholds,
and the specific attack and measurement conditions under consideration. It should therefore
be evaluated experimentally rather than assumed to detect every possible class of FDI attack.

In addition to detection performance, the computational requirements of an anomaly detection
system are important when considering its deployment in practical monitoring environments.
Continuous processing of measurement data may impose constraints on processing latency,
memory usage, numerical precision, and hardware resources. Software-based implementations
provide flexibility for algorithm development and experimental evaluation, but dedicated
hardware platforms such as Field-Programmable Gate Arrays (FPGAs) offer opportunities for
parallel processing, predictable execution, and implementation of specialised digital
signal-processing operations. These characteristics make FPGA technology a relevant platform
for investigating the hardware implementation of statistical detection algorithms.

However, translating statistical algorithms into digital hardware introduces additional
design considerations. Operations involving covariance matrices, multiplication, accumulation,
division, and threshold comparisons must be represented using finite-width numerical formats.
Floating-point algorithms used during software development may therefore require conversion
to fixed-point arithmetic to reduce hardware complexity and resource requirements. Such
conversion must be carefully designed to manage quantisation errors, numerical range,
overflow, and the effect of finite precision on detection decisions. The resulting hardware
architecture must consequently be evaluated not only in terms of logical functionality but
also in terms of resource utilisation, timing characteristics, and the consistency of its
numerical behaviour.

This chapter therefore examines the theoretical and technical foundations relevant to the
development of the proposed Smart Grid False Data Injection Anomaly Detection Engine using
Mahalanobis distance and CUSUM. It begins with an overview of smart-grid architecture and
cybersecurity, followed by a discussion of FDI attacks, their characteristics, and their
implications for power system monitoring. The chapter then reviews conventional bad-data
detection techniques, statistical anomaly detection, Mahalanobis distance, and sequential
change detection using CUSUM. Furthermore, it examines the application of FPGA technology
in embedded detection systems, with particular attention to fixed-point arithmetic and
hardware implementation considerations. Finally, relevant empirical studies are reviewed
and compared to identify the limitations of existing approaches and establish the research
gap addressed by this project.

\section{Smart Grid Architecture and Operation}

\subsection{Overview of Smart Grid Architecture}
A smart grid is an electricity network that integrates conventional power system infrastructure
with modern information and communication technologies to support improved monitoring, control,
automation, and coordination of electrical energy resources. It represents an evolution from
the traditional electricity grid, in which power generation, transmission, distribution, and
consumption were largely coordinated through relatively centralised control arrangements.
In a smart grid environment, intelligent electronic devices, advanced metering infrastructure,
communication networks, automated substations, and computer-based control systems work together
to provide greater visibility of network conditions and support more responsive grid operation.

The architecture of a smart grid is not limited to the physical arrangement of electrical
equipment. It also includes the information infrastructure responsible for collecting,
processing, transmitting, and exchanging operational data between different components of
the power system. Consequently, the smart grid can be considered a cyber-physical system in
which electrical processes and digital information systems interact continuously. The physical
infrastructure is responsible for generating, transmitting, distributing, and consuming
electricity, while the cyber infrastructure supports measurement, communication, supervision,
protection, and control.

The National Institute of Standards and Technology (NIST) developed a conceptual model to
describe the major domains and interactions within the smart grid. The model identifies seven
interconnected domains: Bulk Generation, Transmission, Distribution, Operations, Markets,
Service Providers, and Customers. These domains represent functional areas of the electricity
ecosystem rather than isolated physical locations. They contain different actors, applications,
devices, and communication networks that interact to achieve the overall objectives of the
smart grid \cite{nist2014framework}.

The NIST conceptual model is particularly relevant to understanding smart grid cybersecurity
because it demonstrates that operational information can pass across several organisational
and technical boundaries. A measurement generated by a field device, for example, may be
transmitted through a communication network to a substation controller and subsequently forwarded
to a supervisory control centre. Each stage introduces dependencies on the accuracy, availability,
and integrity of the information being exchanged. Therefore, the reliability of smart grid
operation depends not only on the physical condition of the electrical network but also on the
trustworthiness of the information used by its monitoring and control systems.

\subsection{Major Domains of the Smart Grid}
The seven-domain conceptual model provides a structured representation of the functional
components of a smart grid. As summarized in Table~\ref{tab:smartgrid_domains}, Each domain performs specific responsibilities while exchanging
electrical energy, operational information, or market-related data with other domains. The
interaction among these domains enables coordinated electricity generation, transmission,
distribution, and consumption.

\begin{table}[htbp]
\centering
\caption{Major domains of the NIST smart grid conceptual model.}
\label{tab:smartgrid_domains}
\renewcommand{\arraystretch}{1.3}
\small
\begin{tabular}{|p{3.0cm}|p{5.0cm}|p{6.0cm}|}
\hline
\textbf{Domain} & \textbf{Primary Function} & \textbf{Typical Components or Activities} \\
\hline
Bulk Generation & Produces large quantities of electrical energy for delivery to the transmission network. & Generating stations, plant control systems, generators, and generation monitoring equipment. \\
\hline
Transmission & Transfers electrical energy over long distances at high voltage. & Transmission lines, substations, transformers, protection relays, and wide-area monitoring systems. \\
\hline
Distribution & Delivers electrical energy from substations to end users. & Distribution feeders, reclosers, sectionalizers, distribution transformers, field devices, and distributed generation connections. \\
\hline
Operations & Coordinates and supervises the movement of electricity across the network. & Energy Management Systems (EMS), Distribution Management Systems (DMS), SCADA, and Wide Area Monitoring Systems (WAMS). \\
\hline
Markets & Facilitates the economic exchange of electrical energy and related services. & Electricity market operators, retailers, aggregators, wholesale trading, and market clearing systems. \\
\hline
Service Providers & Provides technical, commercial, and support services to utilities and electricity customers. & Utility service organisations, billing systems, energy service providers, and third-party service platforms. \\
\hline
Customers & Consumes electrical energy and may also generate, store, or manage electricity locally. & Smart meters, customer energy management systems, electric vehicles, rooftop solar systems, and household or industrial loads. \\
\hline
\end{tabular}
\begin{flushleft}
\footnotesize Source: Adapted from the NIST Smart Grid Conceptual Model \cite{nist2014framework}.
\end{flushleft}
\end{table}

The Bulk Generation domain represents the production of electricity from conventional and
renewable energy sources. Generating stations convert different forms of energy into electrical
energy and supply it to the transmission network. Their operation is coordinated through plant
control systems and other monitoring mechanisms that supervise generation parameters and
equipment conditions.

The Transmission domain is responsible for transporting electrical energy from generating stations
to major substations and distribution networks. Because transmission systems operate over large
geographical areas, their monitoring requires information from different substations and
measurement devices. Protection relays, phasor measurement units, remote terminal units, and
other intelligent electronic devices provide information about voltage, current, frequency, and
other operating conditions. These measurements assist operators in understanding the state of
the transmission network and responding to abnormal operating conditions.

The Distribution domain delivers electrical energy from transmission substations to residential,
commercial, and industrial consumers. It includes distribution feeders, transformers, switching
devices, protective equipment, and field monitoring systems. The increasing integration of
distributed energy resources, such as rooftop solar installations, battery storage, and electric
vehicles, has made distribution network management more complex. As a result, distribution systems
increasingly depend on automated monitoring and control technologies to maintain acceptable
voltage levels, manage power flows, and improve service reliability.

The Operations domain coordinates and supervises activities across the electrical network.
It contains systems such as Supervisory Control and Data Acquisition (SCADA), Energy Management
Systems (EMS), Distribution Management Systems (DMS), and Wide Area Monitoring Systems (WAMS).
These systems receive information from field devices and measurement equipment, process the
information, and provide operators with an understanding of the current operating condition of
the grid. Depending on the application, they may also support control actions such as switching
operations, generation adjustments, and responses to abnormal system conditions.

The Markets domain supports the commercial and economic activities associated with electricity
supply and consumption. It facilitates the exchange of information relating to electricity
demand, generation availability, pricing, and energy transactions. Although its primary
responsibility is economic coordination rather than direct electrical protection, it interacts
with operational and energy-supplying domains because market decisions can influence generation
scheduling and electricity demand.

The Service Providers domain consists of organisations and systems that provide services to
electricity utilities and customers. These services may include billing, energy management,
communication support, information processing, and other utility-related applications. Its
interaction with other smart grid domains allows service providers to access relevant operational
or customer information through defined interfaces.

The Customer domain represents the end users of electrical energy. In a traditional electricity
system, customers are mainly viewed as consumers. However, modern smart grid infrastructure
allows customers to participate more actively through smart meters, demand response programmes,
distributed generation, and energy storage. A customer may therefore consume electricity from
the distribution network while also supplying excess energy from a local renewable generation system.

The seven domains are interconnected through electrical and communication infrastructures. The
conceptual model therefore illustrates that smart grid operation depends on cooperation among
different actors and systems rather than the independent operation of individual components \cite{nist2014framework}.

\subsection{Electrical Infrastructure and Power Flow}
The electrical infrastructure of a smart grid consists of the physical equipment responsible
for generating, transmitting, distributing, and consuming electrical energy. Under normal
operating conditions, electrical power flows from generating stations through high-voltage
transmission networks to substations, where voltage levels are reduced for distribution to
end users. Distribution networks then deliver electricity through feeders and transformers to
residential, commercial, and industrial loads.

The transmission and distribution networks contain electrical components whose operating
conditions are represented by measurable quantities. These include voltage magnitude, voltage
angle, current magnitude, active power, reactive power, and system frequency. The values of these
quantities depend on the operating condition of the network, including generation levels, load
demand, network topology, and the electrical characteristics of connected components.

Power system monitoring requires the collection of these measurements to estimate the operating
condition of the network. For example, an unexpected change in voltage magnitude may indicate a
change in load demand, a switching operation, or a possible fault condition. Similarly, changes
in active and reactive power measurements may provide information about power transfer and
network loading.

The relationship between electrical quantities is governed by the physical characteristics of
the power network. In power system analysis, the network is commonly represented using a mathematical
model involving buses, transmission lines, generators, loads, and other electrical components. A
bus represents a connection point within the network, while transmission lines describe the
electrical connections between buses.

These electrical relationships form the basis of power system state estimation. State estimation
uses available measurements and a mathematical model of the network to determine an estimate of
the system's internal operating condition. This process is important because not every electrical
quantity can be measured directly at every point in the network. Instead, a selected set of
measurements is used to estimate the overall state of the system.

The accuracy of the estimated state depends on the reliability of the measurement data and the
suitability of the mathematical model. Consequently, measurement integrity is an important
requirement for dependable smart grid monitoring. Incorrect or manipulated measurements may
cause the monitoring system to produce an inaccurate representation of the actual electrical network.

\subsection{Communication and Information Infrastructure}
In addition to the electrical network, smart grids depend on communication infrastructure to
exchange information among measurement devices, substations, control centres, utility systems,
and customer equipment. Communication networks provide the pathways through which measurement
values, status information, alarms, control commands, and other operational data are transmitted.

These communication infrastructures may include substation Local Area Networks (LANs), Wide
Area Networks (WANs), field communication networks, wireless communication technologies, and
utility enterprise networks. Their purpose is to connect devices and applications that may be
physically separated but must cooperate to support coordinated power system operation.

The communication infrastructure is particularly important for supervisory monitoring. Field
devices collect information from electrical equipment and transmit the information to control
systems. Supervisory systems process the received data and present it to operators, who can
use the information to assess network conditions and initiate appropriate control actions.
Depending on the system architecture, control commands may also be transmitted from the control
centre back to field equipment.

Interoperability is an important requirement in this environment because smart grid components
may be produced by different manufacturers and may use different communication technologies.
Standards such as IEC 61850 provide communication and information modelling approaches for the
exchange of data among substation automation and power system devices. The Smart Grid Architecture
Model (SGAM) also provides a structured way of representing smart grid domains, hierarchical
zones, and interoperability layers \cite{iec61850_sgam}.

The communication infrastructure introduces cybersecurity considerations because the information
exchanged between devices and control systems must be protected against unauthorised modification,
disclosure, interruption, and impersonation. In particular, the integrity of measurement data is
essential because monitoring and control decisions are often based directly on information
received from remote devices.

A communication network may successfully deliver a message while the contents of that message
are incorrect or maliciously modified. Therefore, communication availability alone does not
guarantee the trustworthiness of operational information. Smart grid monitoring systems must
also consider whether received measurements are consistent with expected electrical behaviour
and the statistical characteristics of the operating system.

\subsection{Measurement and Supervisory Monitoring Systems}
Measurement systems provide the data required for monitoring, analysis, and control of
electrical networks. Different devices are deployed across smart grid infrastructure to measure
electrical quantities and communicate their values to monitoring systems.

One important category of measurement equipment is the Phasor Measurement Unit (PMU). PMUs
measure voltage and current phasors and provide time-synchronised measurements that can be used
for wide-area monitoring and power system analysis. Their synchronised measurements allow
operators and analytical systems to observe relationships between electrical quantities at
different locations in the network.

Other measurement and monitoring devices include smart meters, Remote Terminal Units (RTUs),
Intelligent Electronic Devices (IEDs), and sensors installed at substations and distribution
facilities. Smart meters provide information about electricity consumption and may support
advanced metering functions. RTUs collect information from field equipment and communicate with
supervisory systems. IEDs perform functions such as protection, monitoring, automation, and control.

SCADA systems provide supervisory monitoring and control by collecting information from remote
devices and presenting the information to operators. The collected measurements may include
voltage, current, power, frequency, breaker status, and equipment alarms. These values allow
the control centre to monitor the operating condition of the network and respond to operational events.

In more advanced monitoring applications, measurements are processed by state estimation systems
to obtain a consistent estimate of the network operating state. State estimation is particularly
important because raw measurements may contain noise, missing values, communication errors, or
inconsistent readings. The estimation process uses the network model and available measurements
to produce an approximation of the system state.

The measurement process can therefore be viewed as a sequence involving physical observation,
data acquisition, communication, processing, and operational interpretation. Each stage
contributes to the overall reliability of the monitoring system. Errors introduced during
measurement or communication may affect the quality of the information available to the control centre.

For this reason, measurement validation and anomaly detection are important functions in smart
grid monitoring. These mechanisms examine received data to identify values that are inconsistent
with expected system behaviour. Their importance becomes more significant when measurement
abnormalities are deliberately introduced by an attacker rather than caused by ordinary equipment
faults or measurement noise.

\subsection{Operational Importance of Smart Grid Data Integrity}
The effective operation of a smart grid depends on the availability of accurate and trustworthy
measurement information. Monitoring systems use collected data to assess voltage conditions,
estimate power flows, identify abnormal operating conditions, and support operational decisions.
If the information supplied to these systems is inaccurate, the resulting analysis may not
correctly represent the actual state of the electrical network.

Data integrity refers to the protection of information against unauthorised or unintended
modification. In a smart grid environment, this property is particularly important because
measurements exchanged between field devices and control systems may influence decisions
affecting power system operation.

For example, consider a control centre receiving voltage and power measurements from several
substations. If the measurements are accurate, the monitoring system can use them to develop
a reasonable estimate of network conditions. However, if some measurements are modified before
reaching the control centre, the resulting estimate may differ from the actual physical condition
of the network. The operator may consequently make decisions based on misleading information.

This problem is relevant to False Data Injection (FDI) attacks, in which an attacker deliberately
modifies measurement values to influence the output of monitoring or state estimation systems.
Unlike ordinary measurement errors, maliciously manipulated data may be constructed to appear
statistically or mathematically plausible. This makes the identification of FDI attacks more
challenging than simply checking whether an individual measurement exceeds a fixed physical limit.

The need to protect measurement integrity therefore provides an important motivation for
statistical anomaly detection techniques. Such techniques examine the characteristics of
received measurements and determine whether the observed data significantly deviates from an
established reference condition. In addition, sequential monitoring techniques can evaluate
whether deviations persist over time.

Within the context of this research, smart grid architecture provides the operational
environment in which measurement data is generated, transmitted, and analysed. Understanding
the relationship between electrical infrastructure, measurement devices, communication
networks, and supervisory control systems is necessary for identifying where false data
may be introduced and how its effects may be detected.

The proposed detection engine is therefore considered within the broader smart grid monitoring
environment. Its focus is on analysing measurement-related data using Mahalanobis distance
and CUSUM-based statistical monitoring. These techniques are discussed in detail in subsequent
sections of this chapter.

\section{Cybersecurity in Smart Grid Systems}

\subsection{Cyber-Physical Security Objectives: The CIA Triad in Power Systems}
In classical corporate enterprise information technology (IT), cybersecurity prioritizes
confidentiality, followed by integrity and availability. In operational technology (OT)
and power-system control environments, this priority order is fundamentally inverted:
Availability and Integrity take precedence over Confidentiality \cite{nist80082}.
A momentary delay in operational telemetry or control commands can trigger protective
relay misoperations or islanding, while corrupted measurement data can deceive state
estimators into erroneous dispatch actions.

\begin{itemize}
    \item \textbf{Integrity:} Ensures that synchrophasor frames, SCADA measurements,
    and control setpoints are transmitted without unauthorized modification or tampering.
    Integrity violations represent the primary mechanism of False Data Injection attacks.
    \item \textbf{Availability:} Guarantees timely and dependable access to power-grid
    measurements. Under IEEE~C37.118, transmission PMUs report at 50~Hz (every 20~ms);
    excessive network latency or Denial-of-Service (DoS) conditions degrade state estimator
    tracking.
    \item \textbf{Confidentiality:} Prevents eavesdropping on utility communications.
    While telemetry data is often unencrypted due to legacy timing constraints, loss of
    confidentiality enables an adversary to infer grid admittance matrices ($\boldsymbol{H}$),
    which is a prerequisite for crafting stealth FDI vectors.
\end{itemize}

\subsection{Threat Environment and Attack Vectors}
Smart grid communications span multiple geographical and institutional perimeters,
creating diverse attack vectors \cite{musleh2023,alimi2022}:
\begin{enumerate}
    \item \textbf{Substation Local Area Network (LAN) Intrusion:} An attacker gaining
    physical or logical access to a substation Ethernet bus can intercept unauthenticated
    IEC~61850 Sampled Values (SV) or GOOSE messages.
    \item \textbf{Wide-Area Communication Interception:} Synchrophasor streams transmitted
    over routed wide-area networks (WANs) or cellular backup channels can be subject to
    Man-in-the-Middle (MITM) manipulation.
    \item \textbf{GPS Clock Spoofing:} PMUs rely on GPS receiver pulses for microsecond-accurate
    time stamps; spoofing GPS signals alters the apparent phase angle ($\theta$) without
    altering voltage magnitude, inducing artificial state shifts.
    \item \textbf{Compromised Field Hardware:} Malicious firmware modifications in RTUs or
    IEDs can inject false telemetry directly at the acquisition source.
\end{enumerate}

\subsection{Power System Communication Protocols and Vulnerabilities}
Traditional industrial communication protocols deployed in smart grids were conceived
prior to the emergence of modern cyber warfare and frequently lack native cryptographic
safeguards:
\begin{itemize}
    \item \textbf{DNP3 (IEEE 1815) and Modbus/TCP:} Widely utilized in SCADA telemetry,
    these protocols historically transmit data in cleartext without message authentication
    codes (MAC), allowing trivial packet spoofing.
    \item \textbf{IEC 60870-5-104:} Common in European transmission systems; lacks
    encryption and replay protection unless wrapped in TLS tunnels.
    \item \textbf{IEEE C37.118.2:} Specifies binary synchrophasor frames. The standard
    leaves transport-layer security optional to minimize transmission latency, enabling
    adversaries to forge phasor measurements if network boundaries are breached.
\end{itemize}

\subsection{Cybersecurity Standards and Regulatory Frameworks}
To mitigate these vulnerabilities, international standards bodies have formulated
rigorous cybersecurity frameworks. NIST~SP~800-82~Rev.~3 \cite{nist80082} provides
comprehensive guidance on Industrial Control System (ICS) security, categorizing supervisory
monitoring risks. NISTIR~7628 \cite{nist7628,nist7628r1} establishes a multi-volume
framework for smart-grid cybersecurity, emphasizing logical interface boundaries and
defense-in-depth. Similarly, the IEC~62443 series governs security for industrial
automation, mandating security levels (SL1--SL4) across system zones, while ISO/IEC~27001
\cite{iso27001} establishes institutional information security management standards.
Despite these protocols, perimeter defenses cannot entirely prevent insider attacks or
zero-day compromises, establishing the necessity for secondary statistical anomaly
detection engines inside the substation.

\section{False Data Injection Attacks}

\subsection{Principles of False Data Injection}
A False Data Injection (FDI) attack represents an intentional, targeted corruption of
sensor measurements designed to bypass routine validation while inducing a specific error
in the estimated power grid operating state. Let the nominal power system telemetry be
represented by the linear or linearized model:
\begin{equation}
\boldsymbol{z} = \boldsymbol{H}\boldsymbol{x} + \boldsymbol{e},
\label{eq:fdi_clean_model}
\end{equation}
where $\boldsymbol{z} \in \mathbb{R}^m$ is the vector of active/reactive power flows,
power injections, and bus voltages; $\boldsymbol{H} \in \mathbb{R}^{m \times n}$ is the
measurement topology matrix; $\boldsymbol{x} \in \mathbb{R}^n$ is the true state vector
(bus voltage angles and magnitudes); and $\boldsymbol{e} \sim \mathcal{N}(\boldsymbol{0}, \boldsymbol{R})$
denotes measurement noise with covariance $\boldsymbol{R}$.

In an FDI attack, the adversary corrupts the telemetry vector by adding a malicious
perturbation vector $\boldsymbol{a} \in \mathbb{R}^m$:
\begin{equation}
\boldsymbol{z}_a = \boldsymbol{z} + \boldsymbol{a} = \boldsymbol{H}\boldsymbol{x} + \boldsymbol{a} + \boldsymbol{e}.
\label{eq:fdi_attacked_model}
\end{equation}
If $\boldsymbol{a}$ is chosen arbitrarily, it manifests as random bad data and is promptly
rejected by conventional state estimation filters. However, an intelligent adversary
with system knowledge can craft $\boldsymbol{a}$ to evade detection.

\subsection{The Stealth Condition: Evading State Estimation}
As established in foundational work by Liu, Ning, and Reiter \cite{liu2009}, an attack is
termed \textit{stealthy} or \textit{unobservable} if the perturbation vector lies entirely
within the column space of the measurement Jacobian $\boldsymbol{H}$:
\begin{equation}
\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c},
\label{eq:stealth_condition}
\end{equation}
where $\boldsymbol{c} \in \mathbb{R}^n$ represents an arbitrary false state bias vector.
When such an attack is injected, the Weighted Least-Squares (WLS) state estimator
evaluates the attacked state estimate $\hat{\boldsymbol{x}}_a$:
\begin{equation}
\hat{\boldsymbol{x}}_a = (\boldsymbol{H}^T\boldsymbol{R}^{-1}\boldsymbol{H})^{-1}\boldsymbol{H}^T\boldsymbol{R}^{-1}\boldsymbol{z}_a = \hat{\boldsymbol{x}} + (\boldsymbol{H}^T\boldsymbol{R}^{-1}\boldsymbol{H})^{-1}\boldsymbol{H}^T\boldsymbol{R}^{-1}\boldsymbol{H}\boldsymbol{c} = \hat{\boldsymbol{x}} + \boldsymbol{c}.
\end{equation}
The estimated state is shifted exactly by the attacker's bias vector $\boldsymbol{c}$.
Consequently, the post-attack measurement residual vector $\boldsymbol{r}_a$ becomes:
\begin{equation}
\boldsymbol{r}_a = \boldsymbol{z}_a - \boldsymbol{H}\hat{\boldsymbol{x}}_a = (\boldsymbol{z} + \boldsymbol{H}\boldsymbol{c}) - \boldsymbol{H}(\hat{\boldsymbol{x}} + \boldsymbol{c}) = \boldsymbol{z} - \boldsymbol{H}\hat{\boldsymbol{x}} = \boldsymbol{r}.
\end{equation}
Because the post-attack residual $\boldsymbol{r}_a$ is mathematically identical to the
pre-attack residual $\boldsymbol{r}$, all classical residual-based bad data detection
tests fail completely, leaving the attack unobservable to the state estimator.

\subsection{Attack Taxonomy and Temporal Modalities}
Depending on the attacker's operational objectives and execution strategy, FDI attacks
exhibit distinct temporal profiles \cite{habib2023,kumar2022}:
\begin{enumerate}
    \item \textbf{Abrupt / Step FDI Attacks:} The perturbation vector $\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$
    is applied instantaneously at time $t = t_0$. This causes a step change in power flow
    telemetry, intended to trip protective overcurrent relays or trigger rapid generation
    redispatch.
    \item \textbf{Gradual Ramp / Drift FDI Attacks:} The injection magnitude increases
    incrementally over time: $\boldsymbol{a}_t = \beta (t - t_0) \boldsymbol{H}\boldsymbol{c}$
    for $t \ge t_0$. By maintaining an extremely low slope $\beta$, the attacker ensures
    that single-frame rate-of-change checkers are not triggered, slowly shifting the
    system operating point into an insecure state.
    \item \textbf{Multi-Channel False Scaling Attacks:} The attacker scales true measurements
    by a multiplicative factor: $\boldsymbol{z}_{a,t} = (1 + \alpha)\boldsymbol{z}_t$. This
    amplifies real grid fluctuations, misleading automated automatic generation control (AGC)
    loops while maintaining natural signal spectral contours.
    \item \textbf{Historical Replay Attacks:} An adversary intercepts and records a sequence
    of legitimate telemetry during a period of normal, steady-state operation, and replays
    it during an actual physical system event (such as a generator trip or line fault).
    Because the replayed data corresponds to a valid historical physical state, static
    residuals remain small, blinding operators to the emerging physical blackout.
\end{enumerate}

\subsection{Detection Challenges and Theoretical Boundaries}
It is essential to establish a rigorous academic boundary regarding the detectability
of False Data Injection attacks. Combining statistical distance metrics with sequential
monitoring does \textbf{not} automatically guarantee the detection of all stealth FDI attacks.
The effectiveness of any secondary statistical detection mechanism depends fundamentally on:
\begin{itemize}
    \item The specific physical quantities being monitored (e.g., whether local bus voltage
    magnitudes are monitored alongside branch active and reactive power flows).
    \item The degree of correlation between the perturbed channels and unperturbed grid states.
    \item The magnitude of the injected false bias vector $\boldsymbol{c}$ relative to the
    background Gaussian measurement noise variance.
    \item The persistence of the attack across consecutive sampling periods.
\end{itemize}
If an adversary possesses perfect full-network knowledge and injects a bias that shifts
all physical quantities strictly along a valid alternative power-flow equilibrium without
violating operational voltage limits, passive statistical monitoring alone cannot detect
the shift without physical active perturbation (such as dynamic grid watermarking) \cite{wang2023}.
However, when an attack is applied to a subset of localized measurement streams, it
distorts local spatial correlations and temporal dynamics, exposing itself to statistical
detection.

\section{Conventional Bad-Data Detection Techniques}

\subsection{Weighted Least-Squares State Estimation}
Power system state estimation solves for the complex voltage state vector
$\boldsymbol{x} = [\boldsymbol{\theta}^T, \boldsymbol{V}^T]^T$ that minimizes the weighted
sum of squared measurement residuals \cite{abur2004}:
\begin{equation}
\min_{\boldsymbol{x}} J(\boldsymbol{x}) = [\boldsymbol{z} - \boldsymbol{h}(\boldsymbol{x})]^T \boldsymbol{R}^{-1} [\boldsymbol{z} - \boldsymbol{h}(\boldsymbol{x})],
\end{equation}
where $\boldsymbol{h}(\boldsymbol{x})$ represents the non-linear AC power-flow equations
and $\boldsymbol{R} = \text{diag}(\sigma_1^2, \dots, \sigma_m^2)$ is the measurement noise
covariance matrix. In the linearized DC model, $\boldsymbol{h}(\boldsymbol{x}) = \boldsymbol{H}\boldsymbol{x}$,
yielding the closed-form normal equations solution:
\begin{equation}
\hat{\boldsymbol{x}} = (\boldsymbol{H}^T \boldsymbol{R}^{-1} \boldsymbol{H})^{-1} \boldsymbol{H}^T \boldsymbol{R}^{-1} \boldsymbol{z}.
\label{eq:wls_solution}
\end{equation}

\subsection{Measurement Residual Analysis and Chi-Square Detection}
The measurement residual vector $\boldsymbol{r} = \boldsymbol{z} - \boldsymbol{H}\hat{\boldsymbol{x}}$
can be expressed directly as a linear transformation of the measurement vector:
\begin{equation}
\boldsymbol{r} = (\boldsymbol{I} - \boldsymbol{K})\boldsymbol{z},
\end{equation}
where $\boldsymbol{K} = \boldsymbol{H}(\boldsymbol{H}^T \boldsymbol{R}^{-1} \boldsymbol{H})^{-1} \boldsymbol{H}^T \boldsymbol{R}^{-1}$
is the hat matrix. Under nominal Gaussian noise conditions, the residual covariance matrix is
$\boldsymbol{\Omega} = \text{Cov}(\boldsymbol{r}) = (\boldsymbol{I} - \boldsymbol{K})\boldsymbol{R}$.

The classical global bad-data detection test compares the objective function $J(\hat{\boldsymbol{x}})$
against a pre-calculated threshold $\gamma_{\chi^2}$:
\begin{equation}
J(\hat{\boldsymbol{x}}) = \boldsymbol{r}^T \boldsymbol{R}^{-1} \boldsymbol{r} \gtrless \gamma_{\chi^2},
\label{eq:chi2_test}
\end{equation}
where $\gamma_{\chi^2}$ is determined from the chi-square cumulative distribution function
with $m - n$ degrees of freedom for a specified false-alarm probability $\alpha$ (typically $\alpha = 0.01$ or $0.05$):
\begin{equation}
\Pr(J(\hat{\boldsymbol{x}}) \ge \gamma_{\chi^2}) = \alpha.
\end{equation}

\subsection{Largest Normalized Residual (LNR) Test}
When the global chi-square test rejects the hypothesis of clean data, EMS software invokes
the Largest Normalized Residual (LNR) test to identify and isolate specific faulty meters.
The normalized residual for measurement $i$ is defined as:
\begin{equation}
r_{N,i} = \frac{|r_i|}{\sqrt{\Omega_{ii}}} = \frac{|z_i - \boldsymbol{H}_i \hat{\boldsymbol{x}}|}{\sqrt{\Omega_{ii}}},
\end{equation}
where $\Omega_{ii}$ is the $i$-th diagonal element of the residual covariance matrix $\boldsymbol{\Omega}$.
The measurement corresponding to $\max_i r_{N,i}$ is flagged as bad data and removed from
the measurement set, provided $\max_i r_{N,i} > 3.0$ (corresponding to a 99.7\% confidence interval).

\subsection{Mathematical Proof of BDD Blindness to Stealth FDI}
The fatal vulnerability of residual-based BDD to coordinated FDI attacks is proven by
substituting the stealth attack model $\boldsymbol{z}_a = \boldsymbol{z} + \boldsymbol{H}\boldsymbol{c}$
into the residual formulation:
\begin{align}
\boldsymbol{r}_a &= (\boldsymbol{I} - \boldsymbol{K})\boldsymbol{z}_a \nonumber \\
&= (\boldsymbol{I} - \boldsymbol{K})(\boldsymbol{z} + \boldsymbol{H}\boldsymbol{c}) \nonumber \\
&= (\boldsymbol{I} - \boldsymbol{K})\boldsymbol{z} + (\boldsymbol{I} - \boldsymbol{K})\boldsymbol{H}\boldsymbol{c}.
\label{eq:proof_step1}
\end{align}
Expanding the second term:
\begin{align}
(\boldsymbol{I} - \boldsymbol{K})\boldsymbol{H}\boldsymbol{c} &= \boldsymbol{H}\boldsymbol{c} - \boldsymbol{K}\boldsymbol{H}\boldsymbol{c} \nonumber \\
&= \boldsymbol{H}\boldsymbol{c} - \left[ \boldsymbol{H}(\boldsymbol{H}^T \boldsymbol{R}^{-1} \boldsymbol{H})^{-1} \boldsymbol{H}^T \boldsymbol{R}^{-1} \right] \boldsymbol{H}\boldsymbol{c} \nonumber \\
&= \boldsymbol{H}\boldsymbol{c} - \boldsymbol{H} (\boldsymbol{H}^T \boldsymbol{R}^{-1} \boldsymbol{H})^{-1} (\boldsymbol{H}^T \boldsymbol{R}^{-1} \boldsymbol{H}) \boldsymbol{c} \nonumber \\
&= \boldsymbol{H}\boldsymbol{c} - \boldsymbol{H}\boldsymbol{I}\boldsymbol{c} = \boldsymbol{0}.
\label{eq:proof_step2}
\end{align}
Therefore,
\begin{equation}
\boldsymbol{r}_a = \boldsymbol{r} + \boldsymbol{0} = \boldsymbol{r}.
\end{equation}
Because the residual vector $\boldsymbol{r}_a$ remains strictly unaltered, both the global
chi-square statistic ($J(\hat{\boldsymbol{x}}_a) = J(\hat{\boldsymbol{x}})$) and every
normalized residual ($r_{N,i,a} = r_{N,i}$) are completely insensitive to the injection,
proving conclusively that classical BDD cannot detect stealth FDI attacks \cite{liu2009}.

\subsection{Limitations of Residual-Only Monitoring}
The structural failure of classical BDD stems from its exclusive reliance on the measurement
residual $\boldsymbol{r}$. While the residual successfully identifies uncorrelated, random
sensor errors (such as meter calibration drift or communication line dropouts), it possesses
no mechanism to evaluate whether the estimated state itself ($\hat{\boldsymbol{x}}$) is physically
credible or statistically consistent with historical power-system operating distributions.
This fundamental limitation necessitates secondary detection layers that monitor spatial
multivariate correlations and temporal change trajectories.

\section{Statistical Anomaly Detection}

\subsection{Principles of Statistical Process Monitoring in Cyber-Physical Grids}
Statistical anomaly detection in power systems operates on the principle that electrical
grid measurements are governed by underlying physical laws (Ohm's and Kirchhoff's laws)
and continuous operational equilibria. Under nominal operating conditions, telemetry
streams exhibit stationary or cyclostationary probabilistic behaviour characterized by
stable mean vectors and cross-covariance matrices. Cyber-attacks introduce perturbations
that distort these underlying statistical distributions.

\subsection{Univariate versus Multivariate Anomaly Detection}
Univariate anomaly detection monitors each telemetry channel independently against fixed
engineering limits (e.g., verifying that bus voltage satisfies $0.95 \le V_i \le 1.05~\text{p.u.}$).
However, univariate monitoring is fundamentally incapable of detecting sophisticated FDI
attacks. An attacker can easily select state perturbations $\boldsymbol{c}$ such that all
injected measurements remain well within individual operating envelopes.

In contrast, multivariate anomaly detection evaluates the joint probability density function
across multiple interacting channels simultaneously. In a transmission grid, active power flow
$P_{ij}$, reactive power flow $Q_{ij}$, and terminal bus voltages $V_i, V_j$ are physically
coupled through line admittance parameters. An injection vector $\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$
that alters active power flow without inducing the corresponding physical voltage drop
severely violates the joint multi-channel covariance structure, enabling multivariate
statistical detectors to flag anomalies even when individual measurements appear legitimate.

\subsection{Stationary Baselines versus Power System Dynamics}
A critical requirement in statistical monitoring is distinguishing legitimate grid dynamics
(such as daily load curves, capacitor bank switching, or renewable generation fluctuations)
from malicious cyber intrusions. Legitimate operational variations typically occur within
well-defined correlation subspaces. By calibrating statistical reference parameters
($\boldsymbol{\mu}, \boldsymbol{\Sigma}$) over clean historical operational windows, the
anomaly detection engine establishes a baseline of normal physical behaviour. However, as
emphasized throughout this study, the detection performance is strictly bounded by the
validity and stationarity of this reference model.

\subsection{Spatial Correlation versus Temporal Persistence}
An effective defense architecture must address two distinct dimensions of anomaly manifestation:
\begin{enumerate}
    \item \textbf{Spatial Dimension:} Evaluates instantaneous multivariate consistency across
    spatially distributed sensors at a single time step $t$.
    \item \textbf{Temporal Dimension:} Evaluates the historical accumulation of subtle
    deviations across successive time steps $t, t+1, \dots, t+k$.
\end{enumerate}
Neither spatial nor temporal analysis alone provides a complete solution. A spatial detector
detects large abrupt changes instantly but misses slow ramps. A temporal detector captures
gradual drifts but exhibits higher detection delay on abrupt shifts. Combining both modalities
yields a synergistic, complementary defense.

\section{Mahalanobis Distance}

\subsection{Mathematical Definition and Covariance Weighting}
Introduced by P.~C. Mahalanobis in 1936 \cite{mahalanobis1936}, the Mahalanobis distance
is a multivariate metric that measures the statistical divergence of an observation vector
$\boldsymbol{q} \in \mathbb{R}^d$ from a reference distribution characterized by mean vector
$\boldsymbol{\mu} \in \mathbb{R}^d$ and covariance matrix $\boldsymbol{\Sigma} \in \mathbb{R}^{d \times d}$:
\begin{equation}
D_M(\boldsymbol{q}) = \sqrt{(\boldsymbol{q} - \boldsymbol{\mu})^T \boldsymbol{\Sigma}^{-1} (\boldsymbol{q} - \boldsymbol{\mu})}.
\label{eq:mahalanobis_def}
\end{equation}
In digital hardware implementations, the squared Mahalanobis distance $D^2 = D_M^2$ is
preferred to eliminate the computationally expensive square-root operation:
\begin{equation}
D^2 = (\boldsymbol{q} - \boldsymbol{\mu})^T \boldsymbol{W} (\boldsymbol{q} - \boldsymbol{\mu}),
\label{eq:mahalanobis_squared}
\end{equation}
where $\boldsymbol{W} = \boldsymbol{\Sigma}^{-1}$ is the precision or inverse covariance matrix.

\subsection{Geometric Interpretation and Whitening Transformation}
Geometrically, the classical Euclidean distance $\|\boldsymbol{q} - \boldsymbol{\mu}\|_2$
defines spherical contours of equal distance, implicitly assuming that all features are
uncorrelated and possess equal variance. In contrast, the Mahalanobis distance defines
hyper-ellipsoidal contours aligned with the eigenvectors of the covariance matrix
$\boldsymbol{\Sigma}$.

The Mahalanobis metric effectively executes a whitening transformation. By decomposing the
covariance matrix via spectral factorization $\boldsymbol{\Sigma} = \boldsymbol{V} \boldsymbol{\Lambda} \boldsymbol{V}^T$,
where $\boldsymbol{V}$ is the orthonormal eigenvector matrix and $\boldsymbol{\Lambda} = \text{diag}(\lambda_1, \dots, \lambda_d)$
contains the eigenvalues, the measurement deviation $\boldsymbol{r} = \boldsymbol{q} - \boldsymbol{\mu}$
is rotated into principal components and normalized by variance:
\begin{equation}
D^2 = \boldsymbol{r}^T \boldsymbol{V} \boldsymbol{\Lambda}^{-1} \boldsymbol{V}^T \boldsymbol{r} = \sum_{i=1}^d \frac{(\boldsymbol{v}_i^T \boldsymbol{r})^2}{\lambda_i}.
\end{equation}
Under the null hypothesis $H_0$ that $\boldsymbol{q} \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$,
the squared statistic $D^2$ exactly follows a central chi-square distribution with $d$ degrees
of freedom ($D^2 \sim \chi^2_d$). The detection threshold $\tau^2$ is determined from the
cumulative distribution function for a chosen false-alarm probability $\alpha$:
\begin{equation}
\tau^2 = \chi^2_{d, 1-\alpha}.
\end{equation}

\subsection{Application to Synchrophasor Measurement Streams}
In this project, the feature vector $\boldsymbol{q}_t \in \mathbb{R}^4$ captures synchrophasor
telemetry from the IEEE 14-bus system: terminal bus voltages $V_1, V_2$, and active/reactive
branch flows $P_{12}, Q_{12}$. Under legitimate power flows, an increase in transmitted active
power $P_{12}$ across the transmission line between Bus 1 and Bus 2 induces a corresponding
voltage drop $(V_1 - V_2)$ governed by line series impedance. Consequently, the off-diagonal
elements of $\boldsymbol{\Sigma}$ exhibit strong physical correlation.

When an adversary injects a coordinated stealth attack $\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$,
the attack satisfies the state-estimator Jacobian $\boldsymbol{H}$ across the entire grid
model, but typically violates the localized high-frequency covariance relationship
$\boldsymbol{\Sigma}^{-1}$ between line power and bus voltage. Consequently, $D^2$ spikes
abruptly beyond $\tau^2$, exposing the attack on the very first clock cycle.

\subsection{Strengths and Inherent Limitations}
\textbf{Strengths:}
\begin{itemize}
    \item Provides instantaneous, single-cycle anomaly detection for abrupt and scaling attacks.
    \item Completely scale-invariant and accounts for disparate physical units (voltage in p.u.,
    power in MW/MVAR).
    \item Fixed-point datapath reduces to a deterministic matrix-vector multiplication and dot product.
\end{itemize}

\textbf{Inherent Limitations:}
\begin{itemize}
    \item Highly sensitive to non-stationary grid operations; if network topology changes
    (e.g., a transmission line trips), the precision matrix $\boldsymbol{W}$ must be recalibrated.
    \item Blind to slow, gradual ramp attacks during their early phases, where instantaneous
    deviations remain well inside the $\tau^2$ confidence ellipsoid.
    \item Does not detect historical replay attacks whose covariance matches legitimate historical states.
\end{itemize}

\section{CUSUM Sequential Change Detection}

\subsection{Page's Cumulative Sum Sequential Test Formulation}
Originally introduced by E.~S. Page in 1954 \cite{page1954}, the Cumulative Sum (CUSUM)
algorithm is a sequential analysis technique designed for continuous quality control and
quickest change-point detection. Unlike fixed-sample hypothesis tests that evaluate single
snapshots, CUSUM continuously integrates historical evidence over time, making it optimal
for detecting small, persistent shifts in the mean of a stochastic process.

\subsection{Two-Sided CUSUM Formulation and Parameter Roles}
In smart grid monitoring, False Data Injection attacks may introduce positive or negative
biases depending on the attacker's intent (e.g., artificially depressing bus voltage to
induce capacitor switching or inflating branch flow to trigger false overload alarms).
Therefore, a two-sided CUSUM detector is required \cite{montgomery2019,huang2016}.

Let $y_n$ be a scalar monitored telemetry feature at discrete time step $n$, with nominal
in-control mean $\nu_0$. The two-sided recursive CUSUM equations are defined as:
\begin{align}
S_n^+ &= \max\left(0, S_{n-1}^+ + (y_n - \nu_0) - k\right), \label{eq:cusum_pos} \\
S_n^- &= \max\left(0, S_{n-1}^- - (y_n - \nu_0) - k\right), \label{eq:cusum_neg}
\end{align}
with initial conditions $S_0^+ = S_0^- = 0$.

The operational parameters govern the detector's behaviour:
\begin{itemize}
    \item \textbf{Reference Allowance / Slack Parameter ($k$):} Represents the allowable
    drift deadband. For a target detectable mean shift of magnitude $\delta$, statistical
    process control theory dictates setting:
    \begin{equation}
    k = \frac{\delta}{2}.
    \end{equation}
    As long as $|y_n - \nu_0| \le k$, the accumulator terms $(y_n - \nu_0) - k \le 0$,
    preventing spurious accumulation from background Gaussian noise.
    \item \textbf{Decision Threshold ($h$):} The alarm limit. An anomaly is signaled at
    time $n$ if either accumulator exceeds $h$:
    \begin{equation}
    \text{Alarm Asserted if } S_n^+ > h \quad \text{or} \quad S_n^- > h.
    \end{equation}
\end{itemize}

\subsection{Zero-Clamping and Instantaneous Reset}
The $\max(0, \cdot)$ operator in Equations~\eqref{eq:cusum_pos} and \eqref{eq:cusum_neg}
is the defining characteristic of CUSUM. By clamping negative accumulations strictly to zero,
the algorithm prevents negative windup during extended periods of in-control operation.
When a malicious injection begins, the accumulator starts integrating immediately from zero,
eliminating the severe detection lag that plagues standard moving-average or linear low-pass filters.

\subsection{Average Run Length Trade-Off: In-Control ($ARL_0$) versus Out-of-Control ($ARL_1$)}
The performance of a sequential CUSUM detector is characterized by its Average Run Length (ARL):
\begin{itemize}
    \item $\text{ARL}_0$ (In-Control Run Length): The expected number of samples before a
    false alarm is triggered during clean operation ($\delta = 0$). High $\text{ARL}_0$ is
    desired to minimize operational disruption.
    \item $\text{ARL}_1$ (Out-of-Control Run Length): The expected number of samples required
    to trigger an alarm after an attack begins ($\delta > 0$). Low $\text{ARL}_1$ corresponds
    to minimal detection delay.
\end{itemize}
According to Siegmund's approximation \cite{page1954,ross2014}, for continuous Gaussian observations
with variance $\sigma^2$:
\begin{equation}
\text{ARL}_0 \approx \frac{\exp(2 \Delta h') - 2 \Delta h' - 1}{2 \Delta^2}, \quad \text{where } \Delta = \frac{k}{\sigma}, \; h' = h + 1.166\sigma.
\end{equation}
Increasing threshold $h$ exponentially increases $\text{ARL}_0$ (reducing false alarms),
but linearly increases $\text{ARL}_1$ (increasing detection delay). In this project, $h$ and
$k$ are calibrated to achieve $\text{ARL}_0 \ge 100$~frames (2.0~s) while maintaining
$\text{ARL}_1 \le 8$~frames (160~ms) during attack intervals.

\subsection{Strengths and Inherent Limitations of Sequential CUSUM}
\textbf{Strengths:}
\begin{itemize}
    \item Optimal for detecting subtle, persistent gradual drifts and ramp attacks where
    individual samples remain below static spatial thresholds.
    \item Extremely lightweight recursive formulation requiring only subtraction, addition,
    and a comparator, ideal for FPGA logic.
    \item Built-in memory filters high-frequency sensor noise without phase distortion.
\end{itemize}

\textbf{Inherent Limitations:}
\begin{itemize}
    \item Incurs an inevitable multi-sample integration delay on sudden, large step attacks
    relative to instantaneous spatial tests.
    \item Completely blind to attacks whose injected drift rate remains strictly below the
    reference allowance $k$ ($|y_n - \nu_0| < k$).
    \item Requires state memory management (registers or BRAM) to track historical accumulator
    values across multiple PMU channels.
\end{itemize}

\section{FPGA-Based Embedded System Implementation}

\subsection{Motivation for Hardware Acceleration in Substation Monitoring}
Modern transmission substations house hundreds of Intelligent Electronic Devices (IEDs),
digital relays, and PMUs generating high-cadence data streams under the IEEE~C37.118 standard.
While central control-room servers process state estimation every 1 to 5 seconds, localized
substation security engines must inspect incoming telemetry at line rate (within microsecond
intervals) to prevent corrupted packets from entering the local automation bus or tripping
protective breakers \cite{zhang2024}.

General-purpose microprocessors and graphics processing units (GPUs) are poorly suited for
this embedded edge role. Non-deterministic operating system scheduling, thread preemption,
and unpredictable PCIe bus transfers introduce timing jitter ranging from tens of milliseconds
to seconds. Furthermore, high power dissipation (often exceeding 100--250~W) precludes their
use in ruggedized, fanless substation enclosures.

In contrast, Field-Programmable Gate Arrays (FPGAs) provide fully deterministic, microsecond-scale
processing latency, deep spatial pipelining, and high energy efficiency ($< 2.5\text{--}5.0~\text{W}$).
By implementing statistical detection pipelines directly in reconfigurable hardware, every
incoming synchrophasor frame can be ingested, mean-centered, multiplied by the precision matrix,
and evaluated against CUSUM thresholds in a fixed, cycle-accurate schedule.

\subsection{Throughput Requirements for Synchrophasor Line Rates}
Under IEEE~C37.118.1, standard reporting rates ($F_s$) are 50~Hz (for 50~Hz power grids) or
60~Hz (for 60~Hz power grids), corresponding to a packet inter-arrival time of:
\begin{equation}
T_{\text{pmu}} = \frac{1}{F_s} = \frac{1}{50\text{ Hz}} = 20.0~\text{ms} = 20,000~\mu\text{s}.
\end{equation}
In a large substation collecting telemetry from 100 PMU channels simultaneously, an aggregate
line rate requires processing 5,000 frames per second ($200~\mu\text{s}$ per frame). As demonstrated
in subsequent chapters, the proposed SystemVerilog hardware core executes a complete 4-channel
spatial-temporal anomaly evaluation in 36 clock cycles at 100~MHz ($0.36~\mu\text{s}$),
comfortably outperforming line-rate requirements by over $55,000\times$ and allowing a single
FPGA core to time-multiplex thousands of synchrophasor channels.

\subsection{Target FPGA Platform: AMD/Xilinx Artix-7 Architecture}
The target hardware platform selected for this design is the AMD/Xilinx Artix-7
XC7A200T-FBG676-2 FPGA, featured on the AC701 Evaluation Kit \cite{artix7ds}. Built on a
28~nm High-Performance Low-Power (HPL) process, the XC7A200T provides an optimal balance
between high logic density, dedicated arithmetic resources, and ultra-low power consumption.
Its internal architecture comprises:
\begin{itemize}
    \item \textbf{Configurable Logic Blocks (CLBs):} 33,650 slices containing 134,600 six-input
    Look-Up Tables (LUT6) and 269,200 flip-flops (FFs), supporting flexible combinational
    steering logic, state machines, and pipeline registers.
    \item \textbf{DSP48E1 Arithmetic Slices:} 740 dedicated DSP slices, each featuring a
    $25 \times 18$-bit two's-complement multiplier, an independent 48-bit accumulator, and
    a pre-adder, enabling high-speed fixed-point matrix-vector multiplication with zero LUT overhead.
    \item \textbf{Block RAM (BRAM):} 365 dual-port 36~Kb blocks (configurable as 730 independent
    18~Kb RAMB18E1 primitives), offering 13,140~Kb of embedded high-speed storage for multi-channel
    CUSUM accumulator states.
    \item \textbf{Clock Management:} 10 Clock Management Tiles (CMTs), each containing a
    Mixed-Mode Clock Manager (MMCM) and Phase-Locked Loop (PLL) for low-jitter clock synthesis.
\end{itemize}

\subsection{Hardware Architecture Partitioning and Pipelining}
To maximize throughput and ensure deterministic latency, the hardware architecture is
partitioned into decoupled functional stages:
\begin{enumerate}
    \item \textbf{Upstream Handshake & Ingestion Unit:} Latches parallel 64-bit PMU telemetry
    vectors under a standard valid/ready handshake.
    \item \textbf{Preprocessing Stage:} Computes signed deviation residuals $\boldsymbol{r} = \boldsymbol{z} - \boldsymbol{\mu}$
    against pre-loaded calibration registers.
    \item \textbf{Pipelined Mahalanobis Matrix Engine:} Implements four parallel DSP-based
    row-MAC units computing $\boldsymbol{y} = \boldsymbol{W}\boldsymbol{r}$, followed by a
    dot-product unit evaluating $D^2 = \boldsymbol{r}^T \boldsymbol{y}$ over 3 pipeline stages.
    \item \textbf{Recursive CUSUM Filter Core:} Computes two-sided positive and negative
    accumulations with zero-clamping and threshold comparison in a single clock cycle.
    \item \textbf{Time-Multiplexed State BRAM:} Preserves per-channel CUSUM states across
    successive frames using circular addressing.
\end{enumerate}

\section{Fixed-Point Arithmetic and Q-Format Representation}

\subsection{Floating-Point versus Fixed-Point Representation}
While algorithmic prototyping in Python utilizes standard IEEE-754 double-precision (64-bit)
floating-point arithmetic, direct mapping of floating-point units (FPUs) onto FPGA fabric
incurs severe penalties in logic area, routing congestion, and latency. A single double-precision
floating-point multiplier consumes over 500 LUTs and exhibits a 7 to 10 cycle pipeline latency.

Fixed-point arithmetic resolves these limitations by representing fractional quantities
as scaled signed integers. By selecting an appropriate word length and scaling factor,
fixed-point datapaths map directly into dedicated DSP48E1 slices, achieving single-cycle
multiplication, deterministic execution, and minimal dynamic power consumption.

\subsection{Signed Q1.15 Format and Quantization Error Analysis}
The primary numerical format adopted for all input telemetry, calibration matrices, and
intermediate variables is the signed \textbf{Q1.15} fixed-point representation:
\begin{itemize}
    \item Total Word Length: $B = 16$~bits.
    \item Sign Bit: 1 bit ($b_{15}$).
    \item Integer Bits: 0 bits ($I = 0$).
    \item Fractional Bits: 15 bits ($F = 15$).
\end{itemize}
The mathematical value of a 16-bit two's-complement vector $b = [b_{15}, b_{14}, \dots, b_0]$
is given by:
\begin{equation}
X_{\text{real}} = -b_{15} + \sum_{i=0}^{14} b_i 2^{i - 15}.
\end{equation}
The numerical properties of Q1.15 are:
\begin{itemize}
    \item Dynamic Range: $[-1.0, +1.0 - 2^{-15}] = [-1.0, +0.9999694824]$.
    \item Quantization Resolution (LSB Weight): $\Delta = 2^{-15} \approx 3.0517578 \times 10^{-5}$.
    \item Maximum Quantization Error: $\epsilon_{\max} = \frac{\Delta}{2} \approx 1.52588 \times 10^{-5}$.
\end{itemize}
For an input signal uniformly distributed across the full dynamic range, the theoretical
Signal-to-Quantization-Noise Ratio (SQNR) is bounded by:
\begin{equation}
\text{SQNR} \approx 6.02 B_F + 1.76~\text{dB} = 6.02(15) + 1.76 \approx 92.06~\text{dB},
\end{equation}
which vastly exceeds the typical measurement noise floor of utility-grade PMUs
($\approx 0.01\text{--}0.1\% \implies 60\text{--}80~\text{dB}$ SNR).

\subsection{Accumulator Word Length and Dynamic Range Expansion}
When multiplying two signed 16-bit Q1.15 numbers, the intermediate product expands:
\begin{equation}
\text{Q1.15} \times \text{Q1.15} \implies \text{Q2.30 (32 bits)}.
\end{equation}
The resulting product has 2 sign/integer bits and 30 fractional bits, with a dynamic range
of $[-1.0, +1.0)$. In computing the 4-element dot product required for Mahalanobis distance:
\begin{equation}
D^2 = \sum_{j=1}^4 r_j y_j,
\end{equation}
summing four Q2.30 products can cause numerical overflow if intermediate values exceed
the signed representation. To guarantee absolute mathematical headroom against overflow,
the accumulator word length must incorporate guard bits:
\begin{equation}
N_{\text{guard}} = \lceil \log_2(N_{\text{inputs}}) \rceil = \lceil \log_2(4) \rceil = 2~\text{bits}.
\end{equation}
Consequently, the internal accumulator datapath is designed with \textbf{34 bits (Q4.30)},
providing a dynamic range of $[-4.0, +3.9999999]$ and completely eliminating intermediate
accumulation overflow.

\subsection{Convergent Half-Up Rounding and Overflow Saturation Clamping}
Following the 34-bit accumulation stage, the result must be rescaled back to Q1.15 for
subsequent CUSUM filtering and state storage. Direct truncation of the lower 15 fractional
bits introduces a negative DC bias ($-\frac{\Delta}{2}$), which accumulates over time in
recursive filters.

To prevent bias accumulation, the datapath implements \textbf{convergent half-up rounding}
by adding an offset of $+2^{14}$ ($\text{0x0000\_4000}$) to the Q4.30 accumulator before
truncating:
\begin{equation}
Y_{\text{rounded}} = \left\lfloor \frac{X_{\text{acc}} + 2^{14}}{2^{15}} \right\rfloor.
\end{equation}
Furthermore, to protect against arithmetic overflow in two's-complement arithmetic
(specifically the edge case where $-1.0 \times -1.0 = +1.0$, which cannot be represented
in Q1.15), dedicated \textbf{saturation logic} clamps any value exceeding $+0.999969$
strictly to maximum positive full-scale ($\text{0x7FFF}$) and any underflow strictly to
negative full-scale ($\text{0x8000}$).

\section{Review of Related Empirical Studies}

\subsection{Overview of Empirical Literature}
In recent years, the threat of False Data Injection attacks has stimulated extensive
research across the smart grid cybersecurity community. Published detection methodologies
can be broadly categorized into: (a) sequential and CUSUM-based detectors, (b) multivariate
statistical and distance-based detectors, (c) machine learning and deep learning models,
and (d) dedicated FPGA-accelerated hardware architectures.

\subsection{Sequential and CUSUM-Based Anomaly Detectors}
Huang \textit{et al.} (2016) \cite{huang2016} proposed an adaptive CUSUM algorithm for
detecting FDI attacks in smart grid communication networks. Their work demonstrated that
by tuning the reference slack parameter $k$ to the expected mean shift, CUSUM achieves
optimal quickest detection of slow, gradual parameter drifts. However, their formulation
evaluated each telemetry channel independently in software (MATLAB), failing to exploit
cross-channel covariance and suffering from high false-alarm rates during sudden, legitimate
grid switching events.

Foroutan and Salmasi (2021) \cite{foroutan2021} developed a hybrid spatial-clustering and sequential change detection architecture for DC microgrids, while Hasnat and Rahnamay-Naeini (2021) \cite{hasnat2021} formulated graphical spatial-temporal correlation networks for identifying cyber intrusions.

Kumar, Naveen, and Singh (2022) \cite{kumar2022} extended sequential detection by introducing
a multi-channel CUSUM framework for transmission grids. They proved that sequential tests
exhibit bounded detection delay ($\text{ARL}_1 \le 15$ steps) under coordinated ramp attacks.
Nevertheless, their detector operated purely as an offline software script, ignoring execution
latency constraints and fixed-point quantization effects.

Chen, Huang, and Liu (2022) \cite{chen2022} developed a distributed CUSUM test implemented
across local substation monitoring nodes. While their distributed framework successfully
isolated compromised buses, the computational burden on local embedded controllers was not
addressed, and the algorithms assumed idealized double-precision floating-point execution.

\subsection{Multivariate Distance and Correlation-Based Detectors}
Kurt, Y\i lmaz, and Wang (2020) \cite{kurt2020} published a landmark empirical study in
\textit{IEEE Transactions on Information Forensics and Security}, introducing a real-time
decentralized Mahalanobis distance detector for smart grids. Tested on the IEEE 30-bus
system, their detector achieved a 94.2\% detection rate on uncoordinated abrupt FDI attacks
by evaluating the statistical divergence from an empirical covariance matrix. However, because
the test evaluated individual snapshots without temporal memory, its detection probability
degraded sharply ($< 40\%$) when tested against gradual ramp attacks whose trajectory remained
within instantaneous covariance bounds.

Wang, Wu, and Zhang (2023) \cite{wang2023} formulated a physics-informed statistical anomaly
detection method utilizing spatial correlation matrices derived from AC power-flow physics.
Their analysis confirmed that while coordinated stealth attacks ($\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$)
deceive the measurement residual, they introduce subtle violations in high-order cross-bus
voltage correlations. However, their implementation required complex offline matrix inversions,
precluding online adaptation.

\subsection{Machine Learning and Deep Learning Detectors}
With the proliferation of artificial intelligence, numerous researchers have applied
machine learning to FDI detection. Sayghe \textit{et al.} (2021) \cite{sayghe2021} surveyed
over 50 machine-learning detectors, noting that Support Vector Machines (SVM) and Random
Forests achieve detection accuracies exceeding 90\% on static benchmark datasets.

Musleh, Chen, and Dong (2023) \cite{musleh2023} developed a deep recurrent neural network
utilizing Long Short-Term Memory (LSTM) autoencoders to capture temporal and spatial telemetry
dependencies. Evaluated on the IEEE 14-bus benchmark, their model achieved 91.4\% accuracy
and an F1-score of 0.897. Despite these impressive figures, the authors acknowledged severe
deployment limitations: the LSTM autoencoder required a high-end NVIDIA GPU, exhibited an
inference latency of over 52~ms per frame, consumed over 150~W of power, and operated as an
uninterpretable black box lacking formal statistical bounds.

\subsection{Hardware-Accelerated and Embedded Detectors}
The translation of power-grid anomaly detectors into embedded hardware has received growing
attention due to the latency and reliability requirements of modern substations.

Cui, Han, and Zou (2024) \cite{cui2024} implemented an embedded statistical bad-data
detection and identification system on a Texas Instruments TMS320C6678 multicore DSP.
Combining Principal Component Analysis (PCA) with residual $\chi^2$ testing, their engine
achieved an 88.2\% detection rate with a 12~ms execution latency. However, the DSP's
floating-point core consumed 10.5~W and could not meet the sub-millisecond throughput
demands of large synchrophasor networks.

Zhang, Cheng, and Liu (2024) \cite{zhang2024} presented an FPGA-accelerated anomaly detection
architecture for synchrophasor streams in Wide Area Monitoring Systems. Targeting a Xilinx
Kintex-7 device, their design utilized deep pipelining to evaluate streaming PMU vectors
in 1.2~$\mu$s. However, their detector focused exclusively on detecting communication dropouts
and uncoordinated additive Gaussian noise, rather than sophisticated stealth FDI attacks
crafted along the grid topology matrix ($\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$).

Li, Shi, and Wang (2023) \cite{li2023} investigated hardware-efficient fixed-point matrix
multiplication for power-system state estimation on Artix-7 FPGAs. Their findings demonstrated
that signed 16-bit fixed-point arithmetic preserves numerical fidelity comparable to
floating-point units while reducing DSP slice utilization by over 70\%, directly validating
the fixed-point architectural choices adopted in this project.

\section{Comparative Analysis of Existing Approaches}

\subsection{Comparative Evaluation Framework}
To establish the technical contribution of this work relative to the published state of
the art, Table~\ref{tab:priorwork} presents a rigorous comparative analysis across six
representative approaches, evaluating detection methodology, target execution platform,
reported detection performance, computational latency, and fundamental limitations.

\begin{table}[H]
\centering
\caption{Comparison of related works in smart grid FDI anomaly detection.}
\label{tab:priorwork}
\small
\renewcommand{\arraystretch}{1.3}
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

\subsection{Detailed Critical Analysis of Prior Works}
The comparative analysis in Table~\ref{tab:priorwork} reinforces several critical insights:
\begin{enumerate}
    \item \textbf{Residual-Only Vulnerability:} The foundational work of Liu \textit{et al.} \cite{liu2009}
    definitively established that state-estimator residual monitoring ($J(\hat{\boldsymbol{x}}) \gtrless \gamma_{\chi^2}$)
    is fundamentally defective against adversaries with topology awareness ($\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$).
    Any modern defense must incorporate metrics that bypass the residual.
    \item \textbf{Single-Modality Limitations:} Statistical methods that rely solely on spatial
    divergence (such as Kurt \textit{et al.} \cite{kurt2020}) provide outstanding, instantaneous
    detection for abrupt injections but suffer severe degradation when confronted with slow ramp
    attacks. Conversely, methods that rely solely on temporal sequential tests (such as Huang
    \textit{et al.} \cite{huang2016}) detect ramps but suffer cumulative detection delays on abrupt shifts.
    \item \textbf{The Software/Hardware Dichotomy:} Machine learning models (such as Musleh
    \textit{et al.} \cite{musleh2023}) achieve competitive statistical accuracy but impose prohibitive
    computational overhead, non-deterministic latency ($> 50$~ms), and massive energy footprints,
    rendering them impractical for line-rate substation IEDs.
    \item \textbf{The Position of this Work:} Group 9's architecture synthesizes the complementary
    strengths of spatial Mahalanobis distance and temporal two-sided CUSUM into a dedicated
    SystemVerilog core on Artix-7. By achieving a deterministic processing latency of 360~ns
    at 100~MHz and utilizing under 3.5\% of FPGA resources, this work provides a practical,
    hardware-verified bridge between statistical rigor and line-rate embedded execution.
\end{enumerate}

\section{Identified Research Gap}
A systematic review of the published literature reveals a critical, unresolved research gap
at the intersection of smart-grid cybersecurity, statistical process monitoring, and reconfigurable
digital hardware design. While theoretical studies have proposed sophisticated multivariate and
sequential anomaly detection algorithms in software, they almost universally rely on double-precision
floating-point execution and assume unbounded computational time, neglecting the strict microsecond-scale
latency demands and deterministic constraints of substation synchrophasor networks. Conversely,
existing hardware-accelerated detection prototypes on FPGA or DSP platforms have either restricted
their focus to simplistic univariate thresholding—which remains completely vulnerable to coordinated
stealth FDI attacks—or incurred excessive resource footprints without providing formal fixed-point
error bounds and saturation safeguards. Furthermore, prior empirical evaluations frequently evaluate
only a single attack modality (such as abrupt noise), failing to systematically benchmark detection
delays, Average Run Length ($ARL_0/ARL_1$) trade-offs, and ablation performance across diverse,
adversarial attack regimes (including stealth $\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$, gradual
ramps, scaling, and replay). Therefore, an urgent need exists for a fully synthesizable,
hardware-efficient dual-layer statistical anomaly detection architecture that couples instantaneous
covariance-aware Mahalanobis distance with recursive two-sided CUSUM filtering in fixed-point
SystemVerilog, backed by an honest, empirical characterization of detection boundaries and hardware
implementation limits.

\section{Chapter Summary}
This chapter provided a comprehensive review of the theoretical, architectural, and empirical
foundations governing smart grid cybersecurity and anomaly detection. Beginning with the NIST
seven-domain conceptual model and synchrophasor communication infrastructure, the discussion
established the operational criticality of telemetry data integrity. The mathematical mechanics
of False Data Injection attacks were formulated, providing formal proof that coordinate-conforming
attacks ($\boldsymbol{a} = \boldsymbol{H}\boldsymbol{c}$) render conventional residual-based bad
data detection completely blind. Multivariate statistical monitoring via Mahalanobis distance was
reviewed, highlighting its capability to exploit physical power-flow cross-correlations while
identifying its limitation against slow parameter drifts. The recursive formulation of two-sided
CUSUM was examined, demonstrating its optimality for quickest detection of persistent drifts
and the fundamental Average Run Length ($ARL_0/ARL_1$) operational trade-off. FPGA technology
and signed Q1.15 fixed-point arithmetic were analyzed, detailing the necessity of accumulator
guard bits, half-up rounding, and saturation logic. Finally, a structured survey and comparative
table of published works established the explicit research gap addressed by this project.
With these foundations established, Chapter Three presents the detailed mathematical formulation,
fixed-point analysis, and complexity models governing the proposed anomaly detection engine.
"""

print("Chapter 2 module loaded.")
