"""Alert fingerprint generation."""
from __future__ import annotations

import hashlib
import json
from typing import Any


def generate_fingerprint(source: str, labels: dict[str, Any]) -> str:
    """Generate alert fingerprint from source and labels."""
    sorted_labels = dict(sorted(labels.items()))
    fingerprint_data = {"source": source, "labels": sorted_labels}
    fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
    return hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()


def generate_fingerprint_from_alert(alert: dict[str, Any]) -> str:
    """Generate fingerprint from alert dict."""
    return generate_fingerprint(source=alert.get("source", ""), labels=alert.get("labels", {}))
