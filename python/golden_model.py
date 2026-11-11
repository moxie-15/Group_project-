#!/usr/bin/env python3
"""
File: golden_model.py
Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
Description: Bit-accurate Python Golden Reference Model of the SystemVerilog RTL.
             Faithfully implements:
             - Signed Q1.15 arithmetic with rounding and saturation.
             - Matrix-vector multiplication and quadratic Mahalanobis distance.
             - Two-sided recursive CUSUM filters with BRAM state emulation.
             - Spatial, temporal, and aggregated FDI alerts.
             Ingests data/pmu_telemetry.csv and exports data/golden_results.csv.
"""

import os
import json
import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# Bit-Accurate Q1.15 Arithmetic Functions (matching SystemVerilog fdi_pkg.sv)
# -----------------------------------------------------------------------------
def q15_mult(a, b):
    """Signed Q1.15 multiplication with rounding and corner-case saturation."""
    a = int(np.int16(a))
    b = int(np.int16(b))

    # Corner case: -1.0 * -1.0 (0x8000 * 0x8000)
    if a == -32768 and b == -32768:
        return 32767

    # Full 32-bit signed product (Q2.30)
    full_prod = a * b
    # Add half-LSB rounding offset at bit 14
    rounded = full_prod + 0x4000
    # Extract bits [30:15]
    result = (rounded >> 15) & 0xFFFF
    # Interpret as signed 16-bit
    if result >= 0x8000:
        result -= 0x10000
    return int(np.int16(result))

def q15_add_sat(a, b):
    """Signed Q1.15 addition with saturation."""
    s = int(np.int16(a)) + int(np.int16(b))
    return int(np.clip(s, -32768, 32767))

def q15_sub_sat(a, b):
    """Signed Q1.15 subtraction with saturation."""
    d = int(np.int16(a)) - int(np.int16(b))
    return int(np.clip(d, -32768, 32767))

def main():
    print("[*] Running Bit-Accurate Python Golden Reference Model...")

    telemetry_path = "data/pmu_telemetry.csv"
    calib_path = "data/reference/calibration_parameters.json"

    if not os.path.exists(telemetry_path) or not os.path.exists(calib_path):
        raise FileNotFoundError("Missing telemetry or calibration file! Run generate_telemetry.py first.")

    df_in = pd.read_csv(telemetry_path)
    with open(calib_path, "r") as f:
        calib = json.load(f)

    w_matrix = np.array(calib["w_matrix_q15"], dtype=int)
    thresh_t2 = int(calib["thresh_t2_q15"])
    cusum_k = int(calib["cusum_k_q15"])
    cusum_h = int(calib["cusum_h_q15"])
    cusum_nu0 = int(calib["cusum_nu0_q15"])

    n_samples = len(df_in)
    n_channels = 4

    # BRAM State Memory Emulation (4 channels)
    bram_s_pos = np.zeros(n_channels, dtype=int)
    bram_s_neg = np.zeros(n_channels, dtype=int)
    bram_alert_count = np.zeros(n_channels, dtype=int)

    results = []

    for t in range(n_samples):
        # Extract 4-channel measurement vector in Q1.15
        r_vec = np.array([
            df_in.loc[t, "ch0_q15"],
            df_in.loc[t, "ch1_q15"],
            df_in.loc[t, "ch2_q15"],
            df_in.loc[t, "ch3_q15"]
        ], dtype=int)

        # ---------------------------------------------------------------------
        # 1. Mahalanobis Engine: y = W * r, D^2 = r^T * y
        # ---------------------------------------------------------------------
        # Step A: Matrix-vector multiply with 34-bit accumulation
        y_vec = np.zeros(n_channels, dtype=int)
        for i in range(n_channels):
            row_acc = 0
            for j in range(n_channels):
                prod = int(w_matrix[i, j]) * int(r_vec[j]) # 32-bit Q2.30
                row_acc += prod # 34-bit Q4.30
            # Round & saturate to Q1.15
            rounded_row = row_acc + 0x4000
            shifted = rounded_row >> 15
            y_vec[i] = int(np.clip(shifted, -32768, 32767))

        # Step B: Quadratic inner product D^2 = sum(r[i] * y[i])
        dot_acc = 0
        for i in range(n_channels):
            prod = int(r_vec[i]) * int(y_vec[i])
            dot_acc += prod
        rounded_dot = dot_acc + 0x4000
        shifted_dot = rounded_dot >> 15
        dm2_val = int(np.clip(shifted_dot, 0, 32767)) # Non-negative clamp

        spatial_alert = int(dm2_val > thresh_t2)

        # ---------------------------------------------------------------------
        # 2. Time-Multiplexed CUSUM Filter across Channels
        # ---------------------------------------------------------------------
        channel_alerts = []
        for ch in range(n_channels):
            e_in = r_vec[ch]
            s_pos = bram_s_pos[ch]
            s_neg = bram_s_neg[ch]

            # S+ = max(0, S+ + e - nu0 - k)
            delta_pos = int(e_in) - int(cusum_nu0) - int(cusum_k)
            next_pos = s_pos + delta_pos
            next_pos_clamped = int(np.clip(next_pos, 0, 32767))

            # S- = max(0, S- - e + nu0 - k)
            delta_neg = int(cusum_nu0) - int(e_in) - int(cusum_k)
            next_neg = s_neg + delta_neg
            next_neg_clamped = int(np.clip(next_neg, 0, 32767))

            # Update BRAM state
            bram_s_pos[ch] = next_pos_clamped
            bram_s_neg[ch] = next_neg_clamped

            alert_pos = int(next_pos_clamped > cusum_h)
            alert_neg = int(next_neg_clamped > cusum_h)
            ch_cusum_alert = alert_pos or alert_neg
            channel_alerts.append(ch_cusum_alert)

        temporal_alert = int(any(channel_alerts))
        fdi_alert = int(spatial_alert or temporal_alert)

        results.append({
            "sample_idx": t,
            "dm2_metric": dm2_val,
            "spatial_alert": spatial_alert,
            "temporal_alert": temporal_alert,
            "fdi_alert": fdi_alert,
            "s_pos_ch0": bram_s_pos[0],
            "s_neg_ch0": bram_s_neg[0],
            "s_pos_ch1": bram_s_pos[1],
            "s_neg_ch1": bram_s_neg[1],
            "s_pos_ch2": bram_s_pos[2],
            "s_neg_ch2": bram_s_neg[2],
            "s_pos_ch3": bram_s_pos[3],
            "s_neg_ch3": bram_s_neg[3],
            "ground_truth": df_in.loc[t, "attack_label"],
            "attack_type": df_in.loc[t, "attack_type"]
        })

    df_out = pd.DataFrame(results)
    out_path = "data/golden_results.csv"
    df_out.to_csv(out_path, index=False)

    total_alerts = df_out["fdi_alert"].sum()
    total_attacks = df_out["ground_truth"].sum()
    print(f"[+] Golden model evaluation complete. Output saved to {out_path}")
    print(f"[+] Total attack frames in dataset: {total_attacks}")
    print(f"[+] Total FDI alerts triggered: {total_alerts}")

if __name__ == "__main__":
    main()
