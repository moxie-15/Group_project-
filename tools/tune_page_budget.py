import os
import re

# 1. Update chapter_five_generator.py: set figure widths to 0.55\textwidth
with open('chapter_five_generator.py', 'r', encoding='utf-8') as f:
    c5 = f.read()

c5 = re.sub(r'\\reportfigure\[0\.\d+\\textwidth\]', r'\\reportfigure[0.55\\textwidth]', c5)

with open('chapter_five_generator.py', 'w', encoding='utf-8') as f:
    f.write(c5)
print("Updated chapter_five_generator.py figure widths to 0.55\\textwidth")

# 2. Update report_generator_parts.py: combine Declaration and Acknowledgements on one page
with open('report_generator_parts.py', 'r', encoding='utf-8') as f:
    rf = f.read()

# Replace Declaration chapter with clean non-pagebreak combination
old_decl_ack = r"""\chapter*{Declaration}
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
computational infrastructure that supported our modelling and RTL synthesis."""

new_decl_ack = r"""\chapter*{Declaration and Acknowledgements}
\addcontentsline{toc}{chapter}{Declaration and Acknowledgements}

\subsection*{Declaration of Originality}
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

\vspace{0.8cm}
\subsection*{Acknowledgements}
The members of Group 9 express their sincere gratitude to the course
lecturer, the Department of Computer Engineering, and the Faculty of
Engineering at Redeemer's University, Ede, for their academic leadership,
rigorous standards, and the opportunity to undertake this research project.
We also acknowledge the open-source community, IEEE, and the developers of
scientific and power-system computing tools (Python, NumPy, SciPy, Matplotlib,
and MATPOWER) as well as the AMD/Xilinx Vivado Design Suite for providing the
computational infrastructure that supported our modelling and RTL synthesis."""

if old_decl_ack in rf:
    rf = rf.replace(old_decl_ack, new_decl_ack)
    print("Combined Declaration and Acknowledgements in report_generator_parts.py")
else:
    print("Warning: old_decl_ack pattern not found exactly, leaving as-is")

with open('report_generator_parts.py', 'w', encoding='utf-8') as f:
    f.write(rf)

print("Page budget adjustments applied.")

