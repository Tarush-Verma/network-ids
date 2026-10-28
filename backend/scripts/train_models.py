"""
Model Training and Comparative Benchmarking Script
Trains:
  1. Supervised Random Forest Classifier
  2. Unsupervised Isolation Forest Outlier Detector
Evaluates and benchmarks on Test and Zero-Day Unseen datasets:
  - Detection Rate (Recall)
  - False Alarm Rate (FPR)
  - Processing Latency (ms)
  - Generalization to unseen sequences
Saves trained models to backend/saved_models/
"""

import sys
import json
import time
from pathlib import Path
import numpy as np

# Ensure workspace root in path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.data.dataset_loader import DatasetLoader
from backend.app.core.feature_extractor import SequenceFeatureExtractor
from backend.app.models.random_forest import RandomForestDetector
from backend.app.models.isolation_forest import IsolationForestDetector
from backend.app.core.hybrid_engine import HybridIntrusionDetectionEngine


def run_benchmark_on_dataset(engine: HybridIntrusionDetectionEngine, sessions: dict) -> dict:
    """Runs all 3 detectors on each session in dataset and computes comparative metrics."""
    total = len(sessions)
    if total == 0:
        return {}

    fsm_tp = fsm_fp = fsm_tn = fsm_fn = 0
    ml_tp = ml_fp = ml_tn = ml_fn = 0
    hyb_tp = hyb_fp = hyb_tn = hyb_fn = 0

    fsm_latencies = []
    ml_latencies = []
    hyb_latencies = []

    for s_id, events in sessions.items():
        # Ground truth
        is_true_anomaly = any(int(e.get("is_anomaly", 0)) == 1 for e in events)

        fsm_v, ml_v, hyb_v = engine.detect_hybrid(events)

        fsm_latencies.append(fsm_v.latency_ms)
        ml_latencies.append(ml_v.latency_ms)
        hyb_latencies.append(hyb_v.latency_ms)

        # FSM stats
        if is_true_anomaly:
            if fsm_v.is_anomaly: fsm_tp += 1
            else: fsm_fn += 1
        else:
            if fsm_v.is_anomaly: fsm_fp += 1
            else: fsm_tn += 1

        # ML stats
        if is_true_anomaly:
            if ml_v.is_anomaly: ml_tp += 1
            else: ml_fn += 1
        else:
            if ml_v.is_anomaly: ml_fp += 1
            else: ml_tn += 1

        # Hybrid stats
        if is_true_anomaly:
            if hyb_v.is_anomaly: hyb_tp += 1
            else: hyb_fn += 1
        else:
            if hyb_v.is_anomaly: hyb_fp += 1
            else: hyb_tn += 1

    def calc_metrics(tp, fp, tn, fn, latencies):
        recall = tp / max(1, (tp + fn))
        precision = tp / max(1, (tp + fp))
        fpr = fp / max(1, (fp + tn))
        accuracy = (tp + tn) / max(1, (tp + tn + fp + fn))
        f1 = (2 * precision * recall) / max(1e-6, (precision + recall))
        return {
            "accuracy": round(accuracy * 100, 2),
            "recall_detection_rate": round(recall * 100, 2),
            "false_alarm_rate_fpr": round(fpr * 100, 2),
            "precision": round(precision * 100, 2),
            "f1_score": round(f1, 4),
            "avg_latency_ms": round(float(np.mean(latencies)), 4),
            "p95_latency_ms": round(float(np.percentile(latencies, 95)), 4),
            "confusion_matrix": {"TP": tp, "FP": fp, "TN": tn, "FN": fn},
        }

    return {
        "Rule_Based_FSM": calc_metrics(fsm_tp, fsm_fp, fsm_tn, fsm_fn, fsm_latencies),
        "Pure_ML": calc_metrics(ml_tp, ml_fp, ml_tn, ml_fn, ml_latencies),
        "Hybrid": calc_metrics(hyb_tp, hyb_fp, hyb_tn, hyb_fn, hyb_latencies),
    }


def main():
    print("=" * 70)
    print("PHASE 3: TRAINING MACHINE LEARNING MODELS & BENCHMARKING DETECTORS")
    print("=" * 70)

    train_path = Path("backend/data/train_traffic.csv")
    test_path = Path("backend/data/test_traffic.csv")
    zeroday_path = Path("backend/data/zero_day_traffic.csv")
    models_dir = Path("backend/saved_models")
    models_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Training Data
    print("[*] Loading training dataset...")
    train_records = DatasetLoader.load_csv(train_path)
    train_sessions = DatasetLoader.group_by_session(train_records)

    extractor = SequenceFeatureExtractor()
    print(f"[*] Extracting feature vectors ({len(extractor.feature_names)} features) across {len(train_sessions)} sessions...")
    X_train, s_ids_train, y_bin_train, y_cat_train = extractor.extract_batch(train_sessions)

    # 2. Train Random Forest (Supervised Multi-Class)
    print("\n[*] Training Random Forest Supervised Classifier...")
    rf_detector = RandomForestDetector(n_estimators=120, max_depth=14, random_state=42)
    rf_train_metrics = rf_detector.train(X_train, y_cat_train)
    print(f"    - RF Training Accuracy: {rf_train_metrics['accuracy'] * 100:.2f}%")
    print(f"    - RF Classes: {rf_train_metrics['classes']}")

    # 3. Train Isolation Forest (Unsupervised on Normal traffic only)
    print("\n[*] Training Isolation Forest Unsupervised Anomaly Detector...")
    normal_indices = [i for i, label in enumerate(y_cat_train) if label == "Normal"]
    X_train_normal = X_train[normal_indices]
    if_detector = IsolationForestDetector(contamination=0.03, n_estimators=150, random_state=42)
    if_train_metrics = if_detector.train(X_train_normal)
    print(f"    - Trained on {if_train_metrics['samples_trained']} benign sessions.")

    # 4. Save Models
    rf_save_path = models_dir / "rf_detector.joblib"
    if_save_path = models_dir / "if_detector.joblib"
    rf_detector.save(rf_save_path)
    if_detector.save(if_save_path)
    print(f"\n[+] Saved models to: {models_dir}")

    # 5. Initialize Hybrid Engine
    engine = HybridIntrusionDetectionEngine(
        rf_detector=rf_detector,
        if_detector=if_detector,
        feature_extractor=extractor,
    )

    # 6. Evaluate on Test Dataset
    print("\n[*] Benchmarking detectors on Test Dataset (300 sessions)...")
    test_records = DatasetLoader.load_csv(test_path)
    test_sessions = DatasetLoader.group_by_session(test_records)
    test_benchmarks = run_benchmark_on_dataset(engine, test_sessions)

    print("\n" + "-" * 70)
    print(f"{'Detector':<18} | {'Accuracy':<9} | {'Detection Rate':<15} | {'FPR':<8} | {'Latency (ms)':<12}")
    print("-" * 70)
    for name, m in test_benchmarks.items():
        print(f"{name:<18} | {m['accuracy']:>7.2f}% | {m['recall_detection_rate']:>13.2f}% | {m['false_alarm_rate_fpr']:>6.2f}% | {m['avg_latency_ms']:>10.4f} ms")
    print("-" * 70)

    # 7. Evaluate Generalization on Zero-Day Dataset
    print("\n[*] Testing Generalization against Previously Unseen Zero-Day Sequences...")
    zd_records = DatasetLoader.load_csv(zeroday_path)
    zd_sessions = DatasetLoader.group_by_session(zd_records)
    zd_benchmarks = run_benchmark_on_dataset(engine, zd_sessions)

    print("\n" + "-" * 70)
    print("ZERO-DAY GENERALIZATION BENCHMARK (Novel Attacks):")
    for name, m in zd_benchmarks.items():
        print(f"  * {name:<16}: Detection Rate = {m['recall_detection_rate']:>5.1f}% | FPR = {m['false_alarm_rate_fpr']:>4.1f}% | Latency = {m['avg_latency_ms']:.4f} ms")
    print("-" * 70)

    # Save benchmark metrics to JSON for frontend dashboard
    output_benchmark = {
        "test_dataset": test_benchmarks,
        "zeroday_dataset": zd_benchmarks,
        "feature_importances": rf_detector.get_feature_importances(extractor.feature_names)[:10],
        "feature_names": extractor.feature_names,
    }
    benchmark_file = Path("backend/data/benchmark_results.json")
    with open(benchmark_file, "w") as f:
        json.dump(output_benchmark, f, indent=2)
    print(f"\n[+] Saved full comparative benchmark metrics to: {benchmark_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
