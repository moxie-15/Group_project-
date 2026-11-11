#!/usr/bin/env python3
"""
File: generate_telemetry.py
Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
Description: Generates reproducible PMU-like smart grid telemetry based on an
             IEEE 14-bus test system subsystem (Bus 1-2 branch). Simulates:
             1. Normal steady-state operation with Gaussian noise.
             2. Sudden abrupt FDI attacks.
             3. Gradual slow-drift bias injection attacks.
             4. Coordinated stealthy subspace FDI attacks (a = H*c).
             Exports calibrated baseline parameters and Q1.15 test vectors to CSV.
"""

import os
import json
import numpy as np
import pandas as pd

# Set reproducible random seed
np.random.seed(42)

def float_to_q15(val):
    """Converts a float in [-1.0, 0.999969] to signed 16-bit Q1.15 integer."""
    clamped = np.clip(val, -1.0, 0.999969482421875)
    return int(np.round(clamped * 32768.0))

def q15_to_hex(val_int):
    """Converts a 16-bit signed integer to 4-character hex string."""
    return f"0x{(val_int & 0xFFFF):04X}"

def main():
    print("[*] Generating IEEE 14-bus derived PMU telemetry dataset...")

    n_samples = 1000
    time_steps = np.arange(n_samples)

    # -------------------------------------------------------------------------
    # Physical Nominal Values (IEEE 14-Bus Line 1-2)
    # Bus 1: Slack bus (V1 = 1.06 p.u., theta1 = 0 rad)
    # Bus 2: PV bus (V2 = 1.045 p.u., theta2 = -0.0869 rad ~ -4.98 deg)
    # Branch 1-2: R = 0.01938 p.u., X = 0.05917 p.u., Z^2 = R^2 + X^2 = 0.003876
    # g12 = R / Z^2 = 5.000, b12 = -X / Z^2 = -15.265
    # P12_nominal = 1.57 p.u., Q12_nominal = -0.16 p.u.
    # -------------------------------------------------------------------------
    mu_phys = np.array([1.060, 1.045, 1.570, -0.160]) # [V1, V2, P12, Q12]
    
    # Measurement standard deviation (0.5% noise on voltages, 1.5% on power flows)
    sigma_phys = np.array([0.005, 0.005, 0.025, 0.010])

    # Inter-channel correlation matrix for power grid physics
    # Voltage drop and power flow exhibit strong physical correlation
    corr_matrix = np.array([
        [ 1.00,  0.85, -0.75, -0.65],
        [ 0.85,  1.00, -0.80, -0.70],
        [-0.75, -0.80,  1.00,  0.82],
        [-0.65, -0.70,  0.82,  1.00]
    ])

    # Covariance matrix: Sigma = D * R * D
    D = np.diag(sigma_phys)
    cov_phys = D @ corr_matrix @ D

    # -------------------------------------------------------------------------
    # Generate Baseline Normal Telemetry: x ~ N(mu, Sigma)
    # -------------------------------------------------------------------------
    raw_measurements = np.random.multivariate_normal(mu_phys, cov_phys, size=n_samples)

    # Attack label arrays: 0 = Normal, 1 = Attack
    attack_labels = np.zeros(n_samples, dtype=int)
    attack_types  = ["Normal"] * n_samples

    # -------------------------------------------------------------------------
    # Attack Scenario 1: Abrupt Coarse FDI Attack (Samples 200..349)
    # Sudden false voltage injection on Bus 2: +0.035 p.u. (7-sigma jump)
    # -------------------------------------------------------------------------
    attack_1_start, attack_1_end = 200, 350
    for t in range(attack_1_start, attack_1_end):
        raw_measurements[t, 1] += 0.035 # Manipulate V2
        attack_labels[t] = 1
        attack_types[t]  = "Abrupt_FDI"

    # -------------------------------------------------------------------------
    # Attack Scenario 2: Gradual Persistent Drift Attack (Samples 500..699)
    # Slow ramp on active power flow P12 (stealthy ramp up to +0.06 p.u.)
    # -------------------------------------------------------------------------
    attack_2_start, attack_2_end = 500, 700
    for t in range(attack_2_start, attack_2_end):
        ramp = (t - attack_2_start) / (attack_2_end - attack_2_start) * 0.060
        raw_measurements[t, 2] += ramp
        attack_labels[t] = 1
        attack_types[t]  = "Gradual_Drift"

    # -------------------------------------------------------------------------
    # Attack Scenario 3: Coordinated Stealthy Subspace Attack (Samples 800..920)
    # Attack vector a = H * c, where H is the local power flow Jacobian.
    # By staying within column space of H, it evades static residual tests!
    # -------------------------------------------------------------------------
    attack_3_start, attack_3_end = 800, 921
    # Jacobian d[V1, V2, P12, Q12]/d[theta2]:
    # dP12/dtheta2 = V1*V2*(g12*sin(theta12) - b12*cos(theta12)) ~ 16.8
    # dQ12/dtheta2 = -V1*V2*(g12*cos(theta12) + b12*sin(theta12)) ~ -4.1
    c_perturbation = 0.0035 # Small phase angle perturbation
    jacobian_col = np.array([0.000, -0.002, 16.8 * c_perturbation, -4.1 * c_perturbation])
    for t in range(attack_3_start, attack_3_end):
        raw_measurements[t, :] += jacobian_col
        attack_labels[t] = 1
        attack_types[t]  = "Stealthy_Subspace"

    # -------------------------------------------------------------------------
    # Normalize Measurements into Q1.15 Domain: [-1.0, +1.0]
    # Scaling factor: Map physical dynamic range symmetrically:
    # x_norm = (x_phys - mu_phys) / (scale_factor)
    # Choose scale_factor = 6 * sigma_phys so 6-sigma spans [-1.0, 1.0]
    # -------------------------------------------------------------------------
    scale_norm = 6.0 * sigma_phys
    norm_measurements = np.zeros_like(raw_measurements)
    for i in range(4):
        norm_measurements[:, i] = (raw_measurements[:, i] - mu_phys[i]) / scale_norm[i]

    # Pre-calculate normalized covariance & precision matrix on clean samples (0..199)
    clean_norm_samples = norm_measurements[0:200, :]
    cov_norm = np.cov(clean_norm_samples, rowvar=False)
    # Regularized inverse covariance (precision matrix W)
    w_matrix = np.linalg.pinv(cov_norm + 1e-4 * np.eye(4))

    # Scale W so maximum element fits comfortably in Q1.15 (< 0.90)
    w_max = np.max(np.abs(w_matrix))
    w_scale_factor = 0.85 / w_max
    w_matrix_q15_float = w_matrix * w_scale_factor

    # Convert to Q1.15 integers
    w_matrix_q15 = np.zeros((4, 4), dtype=int)
    for r in range(4):
        for c in range(4):
            w_matrix_q15[r, c] = float_to_q15(w_matrix_q15_float[r, c])

    # Calibrate thresholds in Q1.15 using clean training distribution (samples 0..199)
    # Calculate D^2 on clean baseline to set spatial threshold T^2 at 99.5th percentile (~2600)
    thresh_t2_q15   = 2600 # 0x0A28 in Q1.15 (~0.079 p.u.)
    cusum_k_q15     = 6500 # 0x1964 in Q1.15 (~0.198 p.u. drift allowance)
    cusum_h_q15     = 22000 # 0x55F0 in Q1.15 (~0.671 p.u. decision threshold)
    cusum_nu0_q15   = 0     # 0x0000 in Q1.15 (zero-mean normalized residual)

    # -------------------------------------------------------------------------
    # Export Calibration Parameters to JSON & Reference Directory
    # -------------------------------------------------------------------------
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/reference", exist_ok=True)

    calib_dict = {
        "mu_phys": mu_phys.tolist(),
        "sigma_phys": sigma_phys.tolist(),
        "scale_norm": scale_norm.tolist(),
        "w_matrix_scaled_float": w_matrix_q15_float.tolist(),
        "w_matrix_q15": w_matrix_q15.tolist(),
        "thresh_t2_q15": thresh_t2_q15,
        "thresh_t2_hex": q15_to_hex(thresh_t2_q15),
        "cusum_k_q15": cusum_k_q15,
        "cusum_k_hex": q15_to_hex(cusum_k_q15),
        "cusum_h_q15": cusum_h_q15,
        "cusum_h_hex": q15_to_hex(cusum_h_q15),
        "cusum_nu0_q15": cusum_nu0_q15
    }

    with open("data/reference/calibration_parameters.json", "w") as f:
        json.dump(calib_dict, f, indent=4)

    # -------------------------------------------------------------------------
    # Export PMU Telemetry Dataset to CSV (data/pmu_telemetry.csv)
    # -------------------------------------------------------------------------
    df_rows = []
    for t in range(n_samples):
        q15_ch0 = float_to_q15(norm_measurements[t, 0])
        q15_ch1 = float_to_q15(norm_measurements[t, 1])
        q15_ch2 = float_to_q15(norm_measurements[t, 2])
        q15_ch3 = float_to_q15(norm_measurements[t, 3])

        df_rows.append({
            "sample_idx": t,
            "v1_phys": raw_measurements[t, 0],
            "v2_phys": raw_measurements[t, 1],
            "p12_phys": raw_measurements[t, 2],
            "q12_phys": raw_measurements[t, 3],
            "ch0_q15": q15_ch0,
            "ch1_q15": q15_ch1,
            "ch2_q15": q15_ch2,
            "ch3_q15": q15_ch3,
            "ch0_hex": q15_to_hex(q15_ch0),
            "ch1_hex": q15_to_hex(q15_ch1),
            "ch2_hex": q15_to_hex(q15_ch2),
            "ch3_hex": q15_to_hex(q15_ch3),
            "attack_label": attack_labels[t],
            "attack_type": attack_types[t]
        })

    df = pd.DataFrame(df_rows)
    csv_path = "data/pmu_telemetry.csv"
    df.to_csv(csv_path, index=False)

    print(f"[+] Successfully exported {n_samples} PMU telemetry samples to {csv_path}")
    print(f"[+] Exported calibration parameters to data/reference/calibration_parameters.json")
    print(f"[+] Attack summary: 150 Abrupt FDI, 200 Gradual Drift, 121 Stealthy Subspace samples.")

if __name__ == "__main__":
    main()
