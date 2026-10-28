"""
Random Forest Supervised Classifier
Classifies network session sequences into Normal or specific attack classes
using sequence, transition, and temporal features.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import joblib
try:
    from sklearn.ensemble._forest import RandomForestClassifier
except ImportError:
    from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score


class RandomForestDetector:
    """
    Supervised Sequence Intrusion Classifier based on Random Forest.
    """

    def __init__(self, n_estimators: int = 100, max_depth: int = 12, random_state: int = 42):
        self.scaler = StandardScaler()
        self.classifier = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            class_weight="balanced",
            n_jobs=1
        )
        self.classes_: List[str] = []
        self.is_trained = False

    def train(self, X: np.ndarray, y: List[str]) -> Dict:
        """
        Fits scaler and Random Forest on feature matrix X and category labels y.
        """
        X_scaled = self.scaler.fit_transform(X)
        self.classifier.fit(X_scaled, y)
        self.classes_ = list(self.classifier.classes_)
        self.is_trained = True

        y_pred = self.classifier.predict(X_scaled)
        acc = accuracy_score(y, y_pred)
        f1 = f1_score(y, y_pred, average="weighted", zero_division=0)

        return {
            "accuracy": float(acc),
            "f1_score": float(f1),
            "classes": self.classes_,
        }

    def predict(self, X: np.ndarray) -> Tuple[List[str], np.ndarray]:
        """
        Predicts attack category and class probability distribution.
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before predicting.")

        X_scaled = self.scaler.transform(X)
        predictions = self.classifier.predict(X_scaled)
        probabilities = self.classifier.predict_proba(X_scaled)

        return list(predictions), probabilities

    def evaluate(self, X: np.ndarray, y_true: List[str]) -> Dict:
        """
        Evaluates classifier performance on unseen test data.
        """
        y_pred, _ = self.predict(X)
        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
        report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

        return {
            "accuracy": float(acc),
            "f1_score": float(f1),
            "report": report,
            "classes": self.classes_,
        }

    def get_feature_importances(self, feature_names: List[str]) -> List[Dict]:
        """Returns sorted list of feature importances."""
        if not self.is_trained:
            return []
        importances = self.classifier.feature_importances_
        sorted_indices = np.argsort(importances)[::-1]
        return [
            {"feature": feature_names[i], "importance": float(importances[i])}
            for i in sorted_indices
        ]

    def save(self, file_path: Path):
        """Serializes model and scaler to disk."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "scaler": self.scaler,
            "classifier": self.classifier,
            "classes": self.classes_,
            "is_trained": self.is_trained,
        }, file_path)

    @classmethod
    def load(cls, file_path: Path) -> "RandomForestDetector":
        """Loads serialized model and scaler from disk."""
        if not file_path.exists():
            raise FileNotFoundError(f"Model file not found: {file_path}")
        data = joblib.load(file_path)
        detector = cls()
        detector.scaler = data["scaler"]
        detector.classifier = data["classifier"]
        detector.classes_ = data["classes"]
        detector.is_trained = data["is_trained"]
        return detector
