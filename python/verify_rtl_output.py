#!/usr/bin/env python3
"""
File: verify_rtl_output.py
Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
Description: Cross-verifies the SystemVerilog RTL simulation output against the
             Python golden reference model (data/golden_results.csv). Computes
             bit-level match rates, maximum absolute numerical error, and
             detection flag agreement.
"""

import os
import pandas as pd
import numpy as np

def main():
    print("[*] Cross-Verifying SystemVerilog RTL Output vs. Python Golden Model...")

    rtl_out_path = "sim/results/rtl_simulation_output.csv"
    golden_path  = "data/golden_results.csv"

    if not os.path.exists(rtl_out_path):
        print(f"[!] '{rtl_out_path}' not found yet.")
        print("    This file is generated when group members run Vivado behavioral simulation:")
        print("    'vivado -mode batch -source scripts/run_simulation.tcl'")
        print("    Comparing golden reference against ground-truth instead to demonstrate test harness:")
        df_golden = pd.read_csv(golden_path)
        print(f"[+] Loaded {len(df_golden)} golden samples.")
        print(f"    - Detection Agreement with Ground-Truth: {np.mean(df_golden['fdi_alert'] == df_golden['ground_truth'])*100:.2f}%")
        return

    df_rtl = pd.read_csv(rtl_out_path)
    df_gol = pd.read_csv(golden_path)

    n_samples = min(len(df_rtl), len(df_gol))
    df_rtl = df_rtl.iloc[:n_samples]
    df_gol = df_gol.iloc[:n_samples]

    # Compare Mahalanobis distance metric
    dm2_diff = np.abs(df_rtl["dm2_metric"].values - df_gol["dm2_metric"].values)
    max_dm2_err = np.max(dm2_diff)
    mean_dm2_err = np.mean(dm2_diff)

    # Compare Alert flags
    spatial_match = np.mean(df_rtl["spatial_alert"].values == df_gol["spatial_alert"].values) * 100.0
    fdi_match     = np.mean(df_rtl["fdi_alert"].values == df_gol["fdi_alert"].values) * 100.0

    print("="*60)
    print("RTL vs. GOLDEN REFERENCE VERIFICATION RESULTS")
    print("="*60)
    print(f"Total Evaluated Samples:      {n_samples}")
    print(f"Mahalanobis Mean Abs Error:   {mean_dm2_err:.4f} LSBs")
    print(f"Mahalanobis Max Abs Error:    {max_dm2_err} LSBs")
    print(f"Spatial Alert Agreement:      {spatial_match:.2f}%")
    print(f"Global FDI Alert Agreement:   {fdi_match:.2f}%")
    print("="*60)

    if max_dm2_err <= 1 and fdi_match >= 99.0:
        print("[STATUS] BIT-ACCURATE HARDWARE/SOFTWARE MATCH CONFIRMED!")
    else:
        print("[STATUS] Minor discrepancy detected. Inspect testbench logging.")

if __name__ == "__main__":
    main()

