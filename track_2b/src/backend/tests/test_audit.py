"""
Unit tests for RelayZero Cryptographic Audit Logger.
"""

from track_2b.src.backend.audit import AuditLogger


def test_audit_log_chaining():
    logger = AuditLogger()
    e1 = logger.log("REPORT_INGESTED", "Dispatcher", {"id": "SRC-01"})
    assert e1.entry_id == "AUD-0001"
    assert e1.hash_prev == "0" * 64
    assert len(e1.hash_curr) == 64

    e2 = logger.log("EXTRACTION_COMPLETED", "Apertus-1.5-8B", {"count": 4})
    assert e2.entry_id == "AUD-0002"
    assert e2.hash_prev == e1.hash_curr

    assert logger.verify_integrity() is True


def test_audit_tampering_detection():
    logger = AuditLogger()
    logger.log("ACTION_1", "UserA", {"data": 1})
    logger.log("ACTION_2", "UserB", {"data": 2})
    logger.log("ACTION_3", "UserC", {"data": 3})

    assert logger.verify_integrity() is True

    # Intentionally tamper with history
    logger.trail[1].details = {"data": 9999}
    assert logger.verify_integrity() is False
