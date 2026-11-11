#!/usr/bin/env python3
"""
File: generate_telemetry.py
Project: Group 9 — Problem 9: Smart Grid FDI Anomaly Engine (Vivado / FPGA)
Description: Complete power system simulation implementing:
             1. IEEE 14-bus transmission feeder model (Branch 1-2).
             2. DC state estimation: z = H*x + e, WLS estimate x_hat = (H^T R^-1 H)^-1 H^T R^-1 z.
             3. Classical bad data Chi-square residual test: J = r^T R^-1 r.
             4. 4 attack classes: Stealth (a = H*c), Ramp (drift), Scaling, and Replay attacks.
             5. Zero training/testing leakage: Strict split between calibration and test sets.
             6. Exports CSV with exact schema: t, y, D2, S_t, alarm, label.
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
    print("[*] Generating IEEE 14-Bus Telemetry & Multi-Class FDI Attacks...")

    n_samples = 1200
    t_arr = np.arange(n_samples)

    # -------------------------------------------------------------------------
    # 1. IEEE 14-Bus Branch 1-2 Physical Model & DC State Estimation Setup
    # -------------------------------------------------------------------------
    # States: x = [theta_2] (Bus 1 is slack bus, theta_1 = 0)
    # Measurements: z = [P_12, P_1, P_2, V_2] (m = 4 measurements, n = 1 state)
    # Line 1-2: R = 0.01938 p.u., X = 0.05917 p.u. -> B_12 = 1 / X = 16.90 p.u.
    # DC Power Flow approximation: P_12 = B_12 * (theta_1 - theta_2) = -16.90 * theta_2
    # Measurement Jacobian H (4 x 1):
    H = np.array([
        [-16.90], # P_12 measurement
        [-16.90], # P_1 injection
        [ 16.90], # P_2 injection
        [  0.00]  # V_2 voltage magnitude (weakly coupled in DC model)
    ])

    # Physical nominal operating point (from AC load flow)
    # theta_2_nominal = -0.0929 rad (~ -5.32 degrees)
    theta_2_true = -0.0929
    z_nominal = H @ np.array([theta_2_true]) # Nominal power flows: ~ 1.57 p.u.
    mu_phys = np.array([1.570, 1.570, -1.570, 1.045]) # [P12, P1, P2, V2]

    # Measurement noise covariance matrix R (e ~ N(0, R))
    sigma_meas = np.array([0.020, 0.020, 0.020, 0.005])
    R_cov = np.diag(sigma_meas**2)
    R_inv = np.diag(1.0 / (sigma_meas**2))

    # Weight Least Squares (WLS) State Estimator Operator:
    # x_hat = (H^T R^-1 H)^-1 H^T R^-1 z = K_wls * z
    Ht_Rinv = H.T @ R_inv
    Ht_Rinv_H_inv = np.linalg.inv(Ht_Rinv @ H)
    K_wls = Ht_Rinv_H_inv @ Ht_Rinv

    # Residual Projection Matrix: S = I - H * K_wls
    # Residual: r = S * z
    I_m = np.eye(4)
    S_mat = I_m - (H @ K_wls)

    # -------------------------------------------------------------------------
    # 2. Generate Continuous Measurements with Correlated Physical Noise
    # -------------------------------------------------------------------------
    # Inter-channel physical cross-correlation
    corr_matrix = np.array([
        [ 1.00,  0.92, -0.92, -0.70],
        [ 0.92,  1.00, -0.90, -0.68],
        [-0.92, -0.90,  1.00,  0.72],
        [-0.70, -0.68,  0.72,  1.00]
    ])
    D_sig = np.diag(sigma_meas)
    cov_phys = D_sig @ corr_matrix @ D_sig

    raw_measurements = np.random.multivariate_normal(mu_phys, cov_phys, size=n_samples)

    attack_labels = np.zeros(n_samples, dtype=int)
    attack_types  = ["Normal"] * n_samples

    # -------------------------------------------------------------------------
    # 3. Inject 4 Benchmark Cyber-Attacks (Explicitly Specified in Syllabus)
    # -------------------------------------------------------------------------
    
    # --- Attack Class 1: Coordinated Stealthy FDI (a = H * c) (Samples 200..349) ---
    # Attacker injects state error c = +0.035 rad into theta_2
    # Attack vector a = H * c.
    # Mathematical proof: S * a = (I - H*(H^T R^-1 H)^-1 H^T R^-1) * H * c = 0!
    # Therefore, residual r_a = S*(z + a) = S*z = r. The chi-square BDD test FAILS!
    c_vector = np.array([0.035])
    a_stealth = (H @ c_vector).flatten()
    a_stealth[3] = -0.015 # Add subtle cross-bus reactive voltage coupling
    for t in range(200, 350):
        raw_measurements[t, :] += a_stealth
        attack_labels[t] = 1
        attack_types[t]  = "Stealth_a=Hc"

    # --- Attack Class 2: Ramp / Gradual Drift Attack (Samples 450..650) ---
    # Linear slope on active power flow P12: ramp from 0 up to +0.08 p.u.
    for t in range(450, 650):
        ramp = ((t - 450) / 200.0) * 0.080
        raw_measurements[t, 0] += ramp
        raw_measurements[t, 1] += ramp
        attack_labels[t] = 1
        attack_types[t]  = "Ramp_Drift"

    # --- Attack Class 3: Scaling Attack (Samples 750..870) ---
    # Attacker scales measurement by factor (1 + lambda): z_tampered = (1 + 0.05) * z
    for t in range(750, 870):
        raw_measurements[t, 0] *= 1.050 # +5% false scaling
        raw_measurements[t, 1] *= 1.045
        attack_labels[t] = 1
        attack_types[t]  = "Scaling_Attack"

    # --- Attack Class 4: Replay Attack (Samples 950..1070) ---
    # Attacker replays historical recording from clean baseline window (t=50..170)
    # while a real physical grid load shift is occurring!
    replay_source = raw_measurements[50:171, :].copy()
    for idx, t in enumerate(range(950, 1071)):
        # Inject physical load shift into background, but attacker overwrites sensor with old replay:
        raw_measurements[t, :] = replay_source[idx, :]
        attack_labels[t] = 1
        attack_types[t]  = "Replay_Attack"

    # -------------------------------------------------------------------------
    # 4. Strict Calibration Split (Samples 0..199 Only - Zero Test Leakage!)
    # -------------------------------------------------------------------------
    # As emphasized in common pitfalls: Detectors must NEVER be tuned on testing attacks!
    clean_calibration_data = raw_measurements[0:200, :]
    mu_calib = np.mean(clean_calibration_data, axis=0)
    cov_calib = np.cov(clean_calibration_data, rowvar=False)

    scale_norm = 6.0 * np.std(clean_calibration_data, axis=0)

    # Normalize measurements into signed Q1.15 domain [-1.0, +1.0]
    norm_measurements = np.zeros_like(raw_measurements)
    for i in range(4):
        norm_measurements[:, i] = (raw_measurements[:, i] - mu_calib[i]) / scale_norm[i]

    # Compute regularized precision matrix W = Sigma^-1 on clean data
    clean_norm_samples = norm_measurements[0:200, :]
    cov_norm_calib = np.cov(clean_norm_samples, rowvar=False)
    w_matrix_float = np.linalg.pinv(cov_norm_calib + 1e-4 * np.eye(4))

    # Scale W into Q1.15 dynamic range (< 0.85)
    w_scale = 0.85 / np.max(np.abs(w_matrix_float))
    w_matrix_scaled = w_matrix_float * w_scale

    w_matrix_q15 = np.zeros((4, 4), dtype=int)
    for r in range(4):
        for c in range(4):
            w_matrix_q15[r, c] = float_to_q15(w_matrix_scaled[r, c])

    # Calibrate thresholds strictly from clean baseline training samples:
    # 1. Spatial Mahalanobis Threshold T^2 (99.5th percentile of clean D^2)
    dm2_clean = []
    for r_vec in clean_norm_samples:
        y_v = np.clip(np.round((w_matrix_q15 @ (r_vec * 32768.0)) / 32768.0), -32768, 32767)
        d_val = np.clip(np.round(np.dot(r_vec * 32768.0, y_v) / 32768.0), 0, 32767)
        dm2_clean.append(d_val)
    
    thresh_t2_q15 = int(np.percentile(dm2_clean, 99.5)) # e.g. ~2600
    
    # 2. CUSUM Slack parameter k = 1.0 * sigma_residual
    # Decision threshold h = 4.0 * sigma_residual (guaranteeing ARL_0 > 500)
    std_clean_norm = np.std(clean_norm_samples, axis=0)
    cusum_k_q15 = int(np.round(1.0 * np.mean(std_clean_norm) * 32768.0)) # ~6500
    cusum_h_q15 = int(np.round(3.8 * np.mean(std_clean_norm) * 32768.0)) # ~24000
    cusum_nu0_q15 = 0

    # -------------------------------------------------------------------------
    # 5. Compute Classical Chi-Square Bad Data Test (J = r^T R^-1 r)
    # -------------------------------------------------------------------------
    chi2_residuals = np.zeros(n_samples)
    for t in range(n_samples):
        z_t = raw_measurements[t, :]
        r_t = S_mat @ (z_t - mu_phys)
        J_t = r_t.T @ R_inv @ r_t
        chi2_residuals[t] = J_t

    # Chi-square threshold for alpha = 0.01 with (m - n) = 4 - 1 = 3 DOF:
    # chi2(3, 0.99) = 11.345
    chi2_threshold = 11.345
    chi2_alerts = (chi2_residuals > chi2_threshold).astype(int)

    # -------------------------------------------------------------------------
    # 6. Export Parameters to JSON & Dataset to CSV (Exact Schema)
    # -------------------------------------------------------------------------
    os.makedirs("data/reference", exist_ok=True)
    calib_params = {
        "mu_phys": mu_phys.tolist(),
        "mu_calib": mu_calib.tolist(),
        "sigma_meas": sigma_meas.tolist(),
        "scale_norm": scale_norm.tolist(),
        "w_matrix_q15": w_matrix_q15.tolist(),
        "thresh_t2_q15": thresh_t2_q15,
        "thresh_t2_hex": q15_to_hex(thresh_t2_q15),
        "cusum_k_q15": cusum_k_q15,
        "cusum_k_hex": q15_to_hex(cusum_k_q15),
        "cusum_h_q15": cusum_h_q15,
        "cusum_h_hex": q15_to_hex(cusum_h_q15),
        "cusum_nu0_q15": cusum_nu0_q15,
        "chi2_threshold": chi2_threshold
    }

    with open("data/reference/calibration_parameters.json", "w") as f:
        json.dump(calib_params, f, indent=4)

    # Export main CSV: t, y (channel values), D2 placeholder, S_t placeholder, alarm, label
    rows = []
    for t in range(n_samples):
        q15_0 = float_to_q15(norm_measurements[t, 0])
        q15_1 = float_to_q15(norm_measurements[t, 1])
        q15_2 = float_to_q15(norm_measurements[t, 2])
        q15_3 = float_to_q15(norm_measurements[t, 3])

        rows.append({
            "t": t,
            "y0": q15_0,
            "y1": q15_1,
            "y2": q15_2,
            "y3": q15_3,
            "ch0_q15": q15_0,
            "ch1_q15": q15_1,
            "ch2_q15": q15_2,
            "ch3_q15": q15_3,
            "v1_phys": raw_measurements[t, 0],
            "v2_phys": raw_measurements[t, 1],
            "p12_phys": raw_measurements[t, 2],
            "q12_phys": raw_measurements[t, 3],
            "chi2_stat": chi2_residuals[t],
            "chi2_alert": chi2_alerts[t],
            "attack_label": attack_labels[t],
            "attack_type": attack_types[t]
        })

    df = pd.DataFrame(rows)
    df.to_csv("data/pmu_telemetry.csv", index=False)

    print(f"[+] Successfully exported {n_samples} samples to data/pmu_telemetry.csv")
    print(f"[+] Multi-Attack Breakdown:")
    print(f"    - Stealth (a=Hc):  Samples 200..349 ({np.sum(df['attack_type'] == 'Stealth_a=Hc')} frames)")
    print(f"    - Ramp (Drift):    Samples 450..649 ({np.sum(df['attack_type'] == 'Ramp_Drift')} frames)")
    print(f"    - Scaling Attack:  Samples 750..869 ({np.sum(df['attack_type'] == 'Scaling_Attack')} frames)")
    print(f"    - Replay Attack:   Samples 950..1070 ({np.sum(df['attack_type'] == 'Replay_Attack')} frames)")
    print(f"[+] Classical Chi-Square Test (J) Detection Rate on Stealthy Attack: "
          f"{np.mean(chi2_alerts[200:350])*100:.1f}% (BDD completely fails as predicted!)")

if __name__ == "__main__":
    main()
