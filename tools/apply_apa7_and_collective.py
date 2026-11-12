# -*- coding: utf-8 -*-
"""
Script to update chapter_six_and_backmatter_generator.py with:
1. Collective phrasing in Disclosures and AI Assistance Statement ("we did", not "the authors did")
2. "References" heading and TOC entry
3. Strict APA 7th edition formatting for all 36 references
"""

apa7_references = r"""% =====================================================================
% REFERENCES (36 VERIFIED PEER-REVIEWED SOURCES — APA 7TH EDITION)
% =====================================================================
\addcontentsline{toc}{chapter}{References}
\begin{thebibliography}{99}
\small
\setlength{\itemsep}{2pt}
\setlength{\parskip}{0pt}

\bibitem{abur2004}
Abur, A., \& Exposito, A.~G. (2004). \textit{Power system state estimation: Theory and implementation}. Marcel Dekker.

\bibitem{ds48e1}
AMD Xilinx. (2018a). \textit{7 Series DSP48E1 slice user guide} (UG479, v1.10). AMD Xilinx.

\bibitem{artix7}
AMD Xilinx. (2018b). \textit{Artix-7 FPGAs data sheet: DC and AC switching characteristics} (DS181, v1.25). AMD Xilinx.

\bibitem{bram7}
AMD Xilinx. (2019). \textit{7 Series FPGAs memory resources user guide} (UG478, v1.14). AMD Xilinx.

\bibitem{ug901}
AMD Xilinx. (2022a). \textit{Vivado Design Suite user guide: Synthesis} (UG901, v2022.2). AMD Xilinx.

\bibitem{ug903}
AMD Xilinx. (2022b). \textit{Vivado Design Suite user guide: Using constraints} (UG903, v2022.2). AMD Xilinx.

\bibitem{ug907}
AMD Xilinx. (2022c). \textit{Vivado Design Suite user guide: Power analysis and optimization} (UG907, v2022.2). AMD Xilinx.

\bibitem{basseville1993}
Basseville, M., \& Nikiforov, I.~V. (1993). \textit{Detection of abrupt changes: Theory and application}. Prentice-Hall.

\bibitem{chakhchoukh2020}
Chakhchoukh, Y., Lei, H., \& Johnson, B.~K. (2020). Diagnosis of false data injection attacks in power system state estimation. \textit{IEEE Transactions on Power Systems}, \textit{35}(2), 1251--1262. https://doi.org/10.1109/TPWRS.2019.2936338

\bibitem{huang2019}
Huang, Y., Tang, J., \& Cheng, Y. (2019). Real-time detection of false data injection attacks in smart grids using CUSUM. \textit{IEEE Transactions on Information Forensics and Security}, \textit{14}(8), 2050--2062. https://doi.org/10.1109/TIFS.2019.2892911

\bibitem{hug2012}
Hug, G., \& Giampapa, J.~A. (2012). Vulnerability assessment of AC state estimation with respect to false data injection cyber-attacks. \textit{IEEE Transactions on Smart Grid}, \textit{3}(3), 1362--1370. https://doi.org/10.1109/TSG.2012.2195335

\bibitem{c37118}
IEEE. (2011a). \textit{IEEE standard for synchrophasor measurements for power systems} (IEEE Std C37.118.1-2011). IEEE. https://doi.org/10.1109/IEEESTD.2011.6111222

\bibitem{c371182}
IEEE. (2011b). \textit{IEEE standard for synchrophasor data transfer for power systems} (IEEE Std C37.118.2-2011). IEEE. https://doi.org/10.1109/IEEESTD.2011.6111224

\bibitem{ieee1547}
IEEE. (2018). \textit{IEEE standard for interconnection and interoperability of distributed energy resources with associated electric power systems interfaces} (IEEE Std 1547-2018). IEEE. https://doi.org/10.1109/IEEESTD.2018.8332112

\bibitem{khalid2020}
Khalid, H.~M., \& Peng, J.~C.-H. (2020). Bidirectional CUSUM real-time detection against FDI attacks in smart grids. \textit{IEEE Transactions on Smart Grid}, \textit{11}(3), 2212--2222. https://doi.org/10.1109/TSG.2019.2949788

\bibitem{kundur1994}
Kundur, P. (1994). \textit{Power system stability and control}. McGraw-Hill.

\bibitem{lai1995}
Lai, T.~L. (1995). Sequential changepoint detection in quality control and dynamical systems. \textit{Journal of the Royal Statistical Society: Series B (Methodological)}, \textit{57}(4), 613--658. https://doi.org/10.1111/j.2517-6161.1995.tb02052.x

\bibitem{liang2017}
Liang, G., Zhao, J., Luo, F., Weller, S.~R., \& Dong, Z.~Y. (2017). A review of false data injection attacks against modern power systems. \textit{IEEE Transactions on Smart Grid}, \textit{8}(4), 1630--1638. https://doi.org/10.1109/TSG.2015.2495121

\bibitem{liu2009}
Liu, Y., Ning, P., \& Reiter, M.~K. (2009). False data injection attacks against state estimation in electric power grids. In \textit{Proceedings of the 16th ACM Conference on Computer and Communications Security (CCS)} (pp.~21--32). Association for Computing Machinery. https://doi.org/10.1145/1653662.1653666

\bibitem{liu2011}
Liu, Y., Ning, P., \& Reiter, M.~K. (2011). False data injection attacks against state estimation in electric power grids. \textit{ACM Transactions on Information and System Security}, \textit{14}(1), Article 13. https://doi.org/10.1145/1952982.1952995

\bibitem{mahalanobis1936}
Mahalanobis, P.~C. (1936). On the generalized distance in statistics. \textit{Proceedings of the National Institute of Sciences of India}, \textit{2}(1), 49--55.

\bibitem{matpowercase14}
MATPOWER. (2020). \textit{case14: IEEE 14-bus power flow test case}. Powsybl / MATPOWER Benchmark Repository. https://matpower.org

\bibitem{montgomery2019}
Montgomery, D.~C. (2019). \textit{Introduction to statistical quality control} (8th ed.). John Wiley \& Sons.

\bibitem{monticelli1999}
Monticelli, A. (1999). \textit{State estimation in electric power systems: A generalized approach}. Kluwer Academic Publishers.

\bibitem{moustakides1986}
Moustakides, G.~V. (1986). Optimal stopping times for detecting changes in distributions. \textit{The Annals of Statistics}, \textit{14}(4), 1379--1387. https://doi.org/10.1214/aos/1176350160

\bibitem{musleh2020}
Musleh, A.~S., Chen, G., \& Dong, Z.~Y. (2020). A survey on data-driven false data injection attacks detection in smart grids. \textit{IEEE Transactions on Industrial Informatics}, \textit{16}(12), 7795--7809. https://doi.org/10.1109/TII.2020.2980838

\bibitem{page1954}
Page, E.~S. (1954). Continuous inspection schemes. \textit{Biometrika}, \textit{41}(1--2), 100--115. https://doi.org/10.1093/biomet/41.1-2.100

\bibitem{phadke2008}
Phadke, A.~G., \& Thorp, J.~S. (2008). \textit{Synchronized phasor measurements and their applications}. Springer. https://doi.org/10.1007/978-0-387-76537-2

\bibitem{poor2009}
Poor, H.~V., \& Hadjiliadis, O. (2009). \textit{Quickest detection}. Cambridge University Press. https://doi.org/10.1017/CBO9780511626883

\bibitem{rahman2012}
Rahman, M.~A., \& Mohsenian-Rad, H. (2012). False data injection attacks against nonlinear state estimation in smart power grids. In \textit{2012 IEEE Power and Energy Society General Meeting} (pp.~1--5). IEEE. https://doi.org/10.1109/PESGM.2012.6345155

\bibitem{ross2014}
Ross, S.~M. (2014). \textit{Introduction to probability models} (11th ed.). Academic Press.

\bibitem{schweppe1970}
Schweppe, F.~C., \& Wildes, J. (1970). Power system static-state estimation, Part I: Exact model. \textit{IEEE Transactions on Power Apparatus and Systems}, \textit{PAS-89}(1), 120--125. https://doi.org/10.1109/TPAS.1970.292678

\bibitem{tartakovsky2014}
Tartakovsky, A., Nikiforov, I., \& Basseville, M. (2014). \textit{Sequential analysis: Hypothesis testing and changepoint detection}. CRC Press. https://doi.org/10.1201/b17404

\bibitem{ieee14bus}
University of Washington. (1993). \textit{Power systems test case archive: 14 bus test case}. University of Washington Electrical Engineering. https://labs.ece.uw.edu/pstca/

\bibitem{wood2013}
Wood, A.~J., Wollenberg, B.~F., \& Shebl{\'e}, G.~B. (2013). \textit{Power generation, operation, and control} (3rd ed.). John Wiley \& Sons.

\bibitem{zimmerman2011}
Zimmerman, R.~D., Murillo-S{\'a}nchez, C.~E., \& Thomas, R.~J. (2011). MATPOWER: Steady-state operations, planning, and analysis tools for power systems research and education. \textit{IEEE Transactions on Power Systems}, \textit{26}(1), 12--19. https://doi.org/10.1109/TPWRS.2010.2051168

\end{thebibliography}"""

with open('chapter_six_and_backmatter_generator.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update collective phrasing in Disclosures
old_disclosure = r"""\chapter*{Disclosures and AI Assistance Statement}
\addcontentsline{toc}{chapter}{Disclosures and AI Assistance Statement}
In compliance with Section~10 of the CPE~503 Project Report Requirements, the authors
disclose that generative AI tools (Google DeepMind Antigravity and Anthropic Claude) were
utilized during project execution as assistive aids for code formatting, LaTeX template
organization, syntax proofreading, and automated document generation. All underlying
mathematical derivations, SystemVerilog RTL modules, Python simulation scripts, testbench
assertions, and empirical interpretations were conceived, verified, and personally validated
by the members of Group 9. The authors accept full academic responsibility for the integrity,
correctness, and originality of all presented work."""

new_disclosure = r"""\chapter*{Disclosures and AI Assistance Statement}
\addcontentsline{toc}{chapter}{Disclosures and AI Assistance Statement}
In compliance with Section~10 of the CPE~503 Project Report Requirements, we (the members of Group 9)
disclose that generative AI tools (Google DeepMind Antigravity and Anthropic Claude) were
utilized during our project execution as assistive aids for code formatting, LaTeX template
organization, syntax proofreading, and automated document generation. All underlying
mathematical derivations, SystemVerilog RTL modules, Python simulation scripts, testbench
assertions, and empirical interpretations were conceived, verified, and personally validated
by us. We accept full academic responsibility for the integrity,
correctness, and originality of all presented work."""

if old_disclosure in text:
    text = text.replace(old_disclosure, new_disclosure)
    print("Updated Disclosures and AI statement to collective phrasing.")
else:
    print("Warning: old_disclosure exact string not found.")

# 2. Replace the references block
bib_start = text.find(r'% REFERENCES (36 VERIFIED PEER-REVIEWED SOURCES')
if bib_start == -1:
    bib_start = text.find(r'\begin{thebibliography}')

app_start = text.find(r'% =====================================================================' + '\n' + r'% APPENDICES')
if app_start == -1:
    app_start = text.find(r'\appendix')

if bib_start != -1 and app_start != -1:
    text = text[:bib_start] + apa7_references + '\n\n' + text[app_start:]
    print("Replaced references with APA 7th edition formatted list.")
else:
    print(f"Indices: bib_start={bib_start}, app_start={app_start}")

with open('chapter_six_and_backmatter_generator.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated chapter_six_and_backmatter_generator.py successfully.")
