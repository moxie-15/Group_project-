# -*- coding: utf-8 -*-
"""
Master script to assemble the complete report.tex and docs/report.tex.
"""

import os
import sys

from report_generator_parts import get_preamble, get_front_matter
from chapter_one_generator import get_chapter_one
from chapter_two_generator import get_chapter_two
from chapter_three_generator import get_chapter_three
from chapter_four_generator import get_chapter_four
from chapter_five_generator import get_chapter_five
from chapter_six_and_backmatter_generator import get_chapter_six_and_backmatter

def assemble_report():
    print("Assembling complete technical report...")
    parts = [
        get_preamble(),
        get_front_matter(),
        get_chapter_one(),
        get_chapter_two(),
        get_chapter_three(),
        get_chapter_four(),
        get_chapter_five(),
        get_chapter_six_and_backmatter()
    ]
    
    full_text = "\n".join(parts)
    
    base_dir = r"C:\Users\MOXIE\Desktop\group_project"
    report_path = os.path.join(base_dir, "report.tex")
    docs_report_path = os.path.join(base_dir, "docs", "report.tex")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"Successfully wrote {len(full_text)} characters to {report_path}")
    
    with open(docs_report_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"Successfully wrote {len(full_text)} characters to {docs_report_path}")

    # Count lines and tables
    lines = full_text.splitlines()
    print(f"Total lines: {len(lines)}")
    table_captions = [l for l in lines if r"\caption" in l and "table" in l.lower()]
    print(f"Found {len(table_captions)} table captions:")
    for tc in table_captions:
        print("  -", tc.strip())

if __name__ == "__main__":
    assemble_report()
