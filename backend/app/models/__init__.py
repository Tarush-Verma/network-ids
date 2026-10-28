"""Machine learning models package."""
from .random_forest import RandomForestDetector
from .isolation_forest import IsolationForestDetector

__all__ = [
    "RandomForestDetector",
    "IsolationForestDetector",
]
