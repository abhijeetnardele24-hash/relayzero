"""
RelayZero Cryptographic Audit Trail.
Maintains a tamper-evident, SHA-256 hash-chained log of all operational events.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
from .schemas import AuditEntry


class AuditLogger:
    def __init__(self, initial_trail: List[AuditEntry] = None):
        self.trail: List[AuditEntry] = initial_trail or []

    def _latest_hash(self) -> str:
        if not self.trail:
            return "0" * 64
        return self.trail[-1].hash_curr

    def log(self, action: str, actor: str, details: Dict[str, Any]) -> AuditEntry:
        timestamp = datetime.now(timezone.utc).isoformat()
        prev_hash = self._latest_hash()
        entry_id = f"AUD-{len(self.trail) + 1:04d}"

        payload = {
            "entry_id": entry_id,
            "timestamp": timestamp,
            "action": action,
            "actor": actor,
            "details": details,
            "hash_prev": prev_hash,
        }
        serialized = json.dumps(payload, sort_keys=True, default=str)
        curr_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            action=action,
            actor=actor,
            details=details,
            hash_prev=prev_hash,
            hash_curr=curr_hash,
        )
        self.trail.append(entry)
        return entry

    def verify_integrity(self) -> bool:
        """Verifies the hash chain from genesis to head."""
        for idx, entry in enumerate(self.trail):
            expected_prev = "0" * 64 if idx == 0 else self.trail[idx - 1].hash_curr
            if entry.hash_prev != expected_prev:
                return False

            payload = {
                "entry_id": entry.entry_id,
                "timestamp": entry.timestamp,
                "action": entry.action,
                "actor": entry.actor,
                "details": entry.details,
                "hash_prev": entry.hash_prev,
            }
            serialized = json.dumps(payload, sort_keys=True, default=str)
            computed_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
            if computed_hash != entry.hash_curr:
                return False
        return True
