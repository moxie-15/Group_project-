#!/usr/bin/env python3
"""
File: run_all.py
Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
Description: Master One-Click Execution Script. Automatically runs the complete
             data generation, bit-accurate modeling, quantitative evaluation,
             and publication visualization pipeline.
Usage: python run_all.py
"""

import sys
import subprocess
import time

def run_step(step_num, title, script_path):
    print("\n" + "="*75)
    print(f"  STEP {step_num}: {title.upper()}")
    print(f"  Executing: python {script_path}")
    print("="*75)
    start_time = time.time()
    
    result = subprocess.run([sys.executable, script_path], capture_output=False)
    elapsed = time.time() - start_time
    
    if result.returncode != 0:
        print(f"\n[ERROR] Step {step_num} failed with return code {result.returncode}!")
        sys.exit(result.returncode)
    else:
        print(f"[SUCCESS] Step {step_num} completed in {elapsed:.2f} seconds.")

def main():
    print("""
    ======================================================================
         GROUP 9: SMART GRID FDI ANOMALY ENGINE (FPGA / VIVADO)
                    MASTER END-TO-END DEMO RUNNER
    ======================================================================
    """)

    run_step(1, "Telemetry Generation (IEEE 14-Bus Feeder & Cyber-Attacks)", "python/generate_telemetry.py")
    run_step(2, "Bit-Accurate Q1.15 Hardware Golden Model", "python/golden_model.py")
    run_step(3, "Quantitative Performance Evaluation & Latency Analysis", "python/evaluate.py")
    run_step(4, "Publication-Grade Figures Rendering (results/)", "python/plots.py")

    print("""
    ======================================================================
                    ALL PIPELINE STEPS COMPLETED SUCCESSFULLY!
    ======================================================================
    [+] Datasets Generated:     data/pmu_telemetry.csv
    [+] Golden Results:         data/golden_results.csv
    [+] Performance Metrics:    results/evaluation_metrics.json
    [+] 6 Analytical Plots:     results/*.png
    [+] SystemVerilog RTL:      rtl/*.sv
    [+] Vivado Automation Tcl:  scripts/*.tcl
    ======================================================================
    """)

if __name__ == "__main__":
    main()
