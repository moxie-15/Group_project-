#!/usr/bin/env python3
"""
File: evaluate.py
Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
Description: Quantitative performance evaluation comparing the proposed
             FPGA Dual-Layer Anomaly Engine (Mahalanobis + CUSUM) against
             conventional baseline detectors (Static Chi-square / Residual test).
             Computes Accuracy, Precision, Recall, F1-Score, FPR, and Latencies.
             Exports results to results/evaluation_metrics.json.
"""

import os
import json
import numpy as np
import pandas as pd

def compute_metrics(predictions, ground_truth):
    """Computes binary classification metrics from predictions and ground truth."""
    tp = int(np.sum((predictions == 1) & (ground_truth == 1)))
    fp = int(np.sum((predictions == 1) & (ground_truth == 0)))
    tn = int(np.sum((predictions == 0) & (ground_truth == 0)))
    fn = int(np.sum((predictions == 0) & (ground_truth == 1)))

    total = len(ground_truth)
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    return {
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1_Score": f1,
        "FPR": fpr,
        "FNR": fnr
    }

def compute_attack_latencies(alerts, df):
    """Calculates detection latency (in samples) for each attack scenario."""
    attack_scenarios = [
        {"name": "Scenario 1: Abrupt FDI", "start": 200, "end": 350},
        {"name": "Scenario 2: Gradual Drift", "start": 500, "end": 700},
        {"name": "Scenario 3: Stealthy Subspace", "start": 800, "end": 921}
    ]

    latencies = {}
    for sc in attack_scenarios:
        window_alerts = alerts[sc["start"]:sc["end"]]
        triggered = np.where(window_alerts == 1)[0]
        if len(triggered) > 0:
            first_trigger = int(triggered[0]) # Delay from start
            latencies[sc["name"]] = {
                "detected": True,
                "latency_samples": first_trigger,
                "start_sample": sc["start"],
                "first_detect_sample": sc["start"] + first_trigger
            }
        else:
            latencies[sc["name"]] = {
                "detected": False,
                "latency_samples": None,
                "start_sample": sc["start"],
                "first_detect_sample": None
            }

    return latencies

def main():
    print("[*] Evaluating Detection Performance & Latency Metrics...")

    os.makedirs("results", exist_ok=True)
    golden_path = "data/golden_results.csv"
    if not os.path.exists(golden_path):
        raise FileNotFoundError(f"{golden_path} not found. Run golden_model.py first.")

    df = pd.read_csv(golden_path)
    ground_truth = df["ground_truth"].values

    # 1. Proposed Dual-Layer Engine (Mahalanobis + CUSUM)
    proposed_alerts = df["fdi_alert"].values
    metrics_proposed = compute_metrics(proposed_alerts, ground_truth)
    latencies_proposed = compute_attack_latencies(proposed_alerts, df)

    # 2. Baseline 1: Mahalanobis Distance Alone (Spatial Chi-Square Residual Test)
    mahal_alone_alerts = df["spatial_alert"].values
    metrics_mahal = compute_metrics(mahal_alone_alerts, ground_truth)
    latencies_mahal = compute_attack_latencies(mahal_alone_alerts, df)

    # 3. Baseline 2: CUSUM Filter Alone (Temporal Trend Detector)
    cusum_alone_alerts = df["temporal_alert"].values
    metrics_cusum = compute_metrics(cusum_alone_alerts, ground_truth)
    latencies_cusum = compute_attack_latencies(cusum_alone_alerts, df)

    # Compile Evaluation Report
    report = {
        "dataset_samples": len(df),
        "attack_samples": int(np.sum(ground_truth)),
        "clean_samples": int(np.sum(ground_truth == 0)),
        "proposed_dual_layer": {
            "metrics": metrics_proposed,
            "latencies": latencies_proposed
        },
        "baseline_mahalanobis_only": {
            "metrics": metrics_mahal,
            "latencies": latencies_mahal
        },
        "baseline_cusum_only": {
            "metrics": metrics_cusum,
            "latencies": latencies_cusum
        }
    }

    report_path = "results/evaluation_metrics.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)

    # Print Formatted Comparison Table
    print("\n" + "="*78)
    print("DETECTION PERFORMANCE COMPARISON SUMMARY")
    print("="*78)
    print(f"{'Metric':<25} | {'Proposed (Dual-Layer)':<20} | {'Mahalanobis Only':<16} | {'CUSUM Only':<12}")
    print("-"*78)
    print(f"{'Accuracy':<25} | {metrics_proposed['Accuracy']*100:>19.2f}% | {metrics_mahal['Accuracy']*100:>15.2f}% | {metrics_cusum['Accuracy']*100:>11.2f}%")
    print(f"{'Precision':<25} | {metrics_proposed['Precision']*100:>19.2f}% | {metrics_mahal['Precision']*100:>15.2f}% | {metrics_cusum['Precision']*100:>11.2f}%")
    print(f"{'Recall (Sensitivity)':<25} | {metrics_proposed['Recall']*100:>19.2f}% | {metrics_mahal['Recall']*100:>15.2f}% | {metrics_cusum['Recall']*100:>11.2f}%")
    print(f"{'F1-Score':<25} | {metrics_proposed['F1_Score']:>20.4f} | {metrics_mahal['F1_Score']:>16.4f} | {metrics_cusum['F1_Score']:>12.4f}")
    print(f"{'False Positive Rate':<25} | {metrics_proposed['FPR']*100:>19.2f}% | {metrics_mahal['FPR']*100:>15.2f}% | {metrics_cusum['FPR']*100:>11.2f}%")
    print(f"{'False Negative Rate':<25} | {metrics_proposed['FNR']*100:>19.2f}% | {metrics_mahal['FNR']*100:>15.2f}% | {metrics_cusum['FNR']*100:>11.2f}%")
    print("-"*78)
    print("DETECTION LATENCY (Time Steps from Attack Injection to First Trigger)")
    print("-"*78)
    for sc_name in latencies_proposed:
        p_lat = latencies_proposed[sc_name]['latency_samples']
        m_lat = latencies_mahal[sc_name]['latency_samples']
        c_lat = latencies_cusum[sc_name]['latency_samples']
        p_str = f"{p_lat} samples" if p_lat is not None else "MISSED"
        m_str = f"{m_lat} samples" if m_lat is not None else "MISSED"
        c_str = f"{c_lat} samples" if c_lat is not None else "MISSED"
        print(f"{sc_name:<25} | {p_str:>20} | {m_str:>16} | {c_str:>12}")
    print("="*78)
    print(f"[+] Evaluation metrics exported to {report_path}")

if __name__ == "__main__":
    main()
