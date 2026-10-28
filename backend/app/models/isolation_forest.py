"""
Isolation Forest Unsupervised Anomaly Detector
Learns benign manifold from normal event sequences and isolates anomalous/zero-day
sequence patterns without prior supervised knowledge.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import joblib
try:
    from sklearn.ensemble._iforest import IsolationForest
except ImportError:
    from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import roc_auc_score, precision_recall_fscore_support


class IsolationForestDetector:
    """
    Unsupervised Outlier & Zero-Day Detector based on Isolation Forests.
    """

    def __init__(self, contamination: float = 0.05, n_estimators: int = 150, random_state: int = 42):
        self.scaler = RobustScaler()
        self.detector = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
            n_jobs=1
        )
        self.is_trained = False

    def train(self, X_normal: np.ndarray) -> Dict:
        """
        Fits RobustScaler and Isolation Forest strictly on benign/normal feature vectors.
        """
        X_scaled = self.scaler.fit_transform(X_normal)
        self.detector.fit(X_scaled)
        self.is_trained = True

        scores = self.detector.score_samples(X_scaled)
        return {
            "samples_trained": len(X_normal),
            "mean_normal_score": float(np.mean(scores)),
            "min_normal_score": float(np.min(scores)),
        }

    def score(self, X: np.ndarray) -> np.ndarray:
        """
        Calculates continuous anomaly scores. Lower scores mean more anomalous.
        Normalized between 0.0 (highly anomalous) and 1.0 (completely normal).
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before scoring.")

        X_scaled = self.scaler.transform(X)
        raw_scores = self.detector.score_samples(X_scaled)

        # Standard score_samples outputs roughly [-0.8, -0.3] or [-0.5, 0.5]
        # We normalize into confidence score: 1.0 = normal, 0.0 = anomaly
        # Using sigmoid-like transformation
        normalized_scores = 1.0 / (1.0 + np.exp(-10.0 * (raw_scores + 0.45)))
        return normalized_scores

    def predict(self, X: np.ndarray) -> Tuple[List[int], np.ndarray]:
        """
        Predicts binary anomaly: 1 for Anomaly, 0 for Normal.
        Returns (predictions, anomaly_scores).
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before predicting.")

        X_scaled = self.scaler.transform(X)
        preds = self.detector.predict(X_scaled)  # 1 for inlier, -1 for outlier

        # Convert to 1 = anomaly, 0 = normal
        binary_preds = [1 if p == -1 else 0 for p in preds]
        scores = self.score(X)

        return binary_preds, scores

    def evaluate(self, X: np.ndarray, y_binary_true: List[int]) -> Dict:
        """
        Evaluates unsupervised anomaly detection performance against true binary labels.
        """
        preds, scores = self.predict(X)
        # Compute precision, recall, f1 for anomaly class (label 1)
        p, r, f1, _ = precision_recall_fscore_support(y_binary_true, preds, average="binary", zero_division=0)

        # AUC-ROC on continuous anomaly metric (1.0 - normal_score)
        anomaly_metric = 1.0 - scores
        try:
            auc = float(roc_auc_score(y_binary_true, anomaly_metric))
        except Exception:
            auc = 0.5

        return {
            "precision": float(p),
            "recall": float(r),
            "f1_score": float(f1),
            "roc_auc": auc,
        }

    def save(self, file_path: Path):
        """Serializes model to disk."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "scaler": self.scaler,
            "detector": self.detector,
            "is_trained": self.is_trained,
        }, file_path)

    @classmethod
    def load(cls, file_path: Path) -> "IsolationForestDetector":
        """Loads serialized model from disk."""
        if not file_path.exists():
            raise FileNotFoundError(f"Model file not found: {file_path}")
        data = joblib.load(file_path)
        detector = cls()
        detector.scaler = data["scaler"]
        detector.detector = data["detector"]
        detector.is_trained = data["is_trained"]
        return detector
