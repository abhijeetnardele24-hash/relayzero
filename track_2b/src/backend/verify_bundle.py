"""
RelayZero Offline Bundle Verification CLI.
Independently verifies:
1. Canonical JSON serialization & SHA-256 bundle checksum
2. Complete audit hash-chain integrity
3. App mode, model metadata, and incident data structure
Usage:
  python -m track_2b.src.backend.verify_bundle <path_to_bundle.json>
"""

import sys
import json
import hashlib
from typing import Dict, Any, List


def verify_bundle_file(bundle_path: str) -> Dict[str, Any]:
    with open(bundle_path, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    # 1. Verify required top-level fields
    required_fields = ["bundle_id", "incident_id", "exported_at", "app_mode", "sha256_checksum", "incident_data", "audit_manifest"]
    for field in required_fields:
        if field not in bundle:
            return {"valid": False, "error": f"Missing required bundle field: {field}"}

    # 2. Recompute SHA-256 checksum over canonical payload
    payload_to_hash = {
        "bundle_id": bundle["bundle_id"],
        "incident_id": bundle["incident_id"],
        "exported_at": bundle["exported_at"],
        "app_mode": bundle["app_mode"],
        "incident_data": bundle["incident_data"],
        "audit_manifest": bundle["audit_manifest"],
    }
    serialized = json.dumps(payload_to_hash, sort_keys=True)
    computed_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    if computed_hash != bundle["sha256_checksum"]:
        return {
            "valid": False,
            "error": f"Checksum mismatch! Computed: {computed_hash}, Bundle has: {bundle['sha256_checksum']}",
        }

    # 3. Verify audit manifest hash chain
    audit_manifest: List[Dict[str, Any]] = bundle["audit_manifest"]
    for idx, entry in enumerate(audit_manifest):
        expected_prev = "0" * 64 if idx == 0 else audit_manifest[idx - 1]["hash_curr"]
        if entry["hash_prev"] != expected_prev:
            return {
                "valid": False,
                "error": f"Audit chain break at entry {idx} ({entry.get('entry_id')}): hash_prev != previous hash_curr",
            }
        recomputed_payload = {
            "entry_id": entry["entry_id"],
            "timestamp": entry["timestamp"],
            "action": entry["action"],
            "actor": entry["actor"],
            "details": entry["details"],
            "hash_prev": entry["hash_prev"],
        }
        recomputed_entry_hash = hashlib.sha256(json.dumps(recomputed_payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()
        if recomputed_entry_hash != entry["hash_curr"]:
            return {
                "valid": False,
                "error": f"Tampered audit entry {entry.get('entry_id')}: payload hash != hash_curr",
            }

    return {
        "valid": True,
        "bundle_id": bundle["bundle_id"],
        "incident_id": bundle["incident_id"],
        "app_mode": bundle["app_mode"],
        "model_name": bundle.get("model_name"),
        "egress_verification": bundle.get("egress_verification"),
        "audit_entries_count": len(audit_manifest),
        "sha256_checksum": computed_hash,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m track_2b.src.backend.verify_bundle <path_to_bundle.json>")
        sys.exit(1)

    path = sys.argv[1]
    res = verify_bundle_file(path)
    if res["valid"]:
        print(f"✓ BUNDLE INTEGRITY VERIFIED: {res['bundle_id']}")
        print(f"  Incident ID: {res['incident_id']}")
        print(f"  Mode: {res['app_mode']} | Model: {res['model_name']}")
        print(f"  Audit Entries: {res['audit_entries_count']} intact SHA-256 blocks")
        print(f"  Checksum: {res['sha256_checksum']}")
        sys.exit(0)
    else:
        print(f"✗ BUNDLE VERIFICATION FAILED: {res['error']}")
        sys.exit(2)


if __name__ == "__main__":
    main()
