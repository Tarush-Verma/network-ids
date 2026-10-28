"""
Dataset Loader & Preprocessing Utility
Loads, validates, and groups raw network packet events into sequence sessions
for feature extraction and model benchmarking.
"""

import csv
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


class DatasetLoader:
    """
    Utility for parsing, grouping, and inspecting network intrusion sequence datasets.
    """

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path

    @staticmethod
    def load_csv(file_path: Path) -> List[Dict]:
        """Loads raw packet rows from a CSV file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found at: {file_path}")

        records = []
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Type cast relevant fields
                row["seq_index"] = int(row["seq_index"])
                row["timestamp"] = float(row["timestamp"])
                row["delta_t"] = float(row["delta_t"])
                row["src_port"] = int(row["src_port"])
                row["dst_port"] = int(row["dst_port"])
                row["payload_size"] = int(row["payload_size"])
                row["is_anomaly"] = int(row["is_anomaly"])
                row["flags"] = row["flags"].split("|") if row["flags"] else []
                records.append(row)

        return records

    @staticmethod
    def group_by_session(records: List[Dict]) -> Dict[str, List[Dict]]:
        """Groups packet events by session_id, ordered by seq_index."""
        sessions = defaultdict(list)
        for r in records:
            sessions[r["session_id"]].append(r)

        for s_id in sessions:
            sessions[s_id].sort(key=lambda x: (x["timestamp"], x["seq_index"]))

        return dict(sessions)

    @classmethod
    def get_summary_statistics(cls, records: List[Dict]) -> Dict:
        """
        Calculates descriptive summary statistics:
        Total packets, total sessions, class distribution, attack breakdown.
        """
        sessions = cls.group_by_session(records)
        attack_counts = defaultdict(int)
        anomaly_count = 0

        for r in records:
            attack_counts[r["attack_category"]] += 1
            if r["is_anomaly"] == 1:
                anomaly_count += 1

        session_lengths = [len(s) for s in sessions.values()]

        return {
            "total_packets": len(records),
            "total_sessions": len(sessions),
            "normal_packets": len(records) - anomaly_count,
            "anomalous_packets": anomaly_count,
            "anomaly_rate_percent": round((anomaly_count / max(1, len(records))) * 100, 2),
            "category_distribution": dict(attack_counts),
            "avg_session_length": round(sum(session_lengths) / max(1, len(session_lengths)), 2),
            "min_session_length": min(session_lengths) if session_lengths else 0,
            "max_session_length": max(session_lengths) if session_lengths else 0,
        }
