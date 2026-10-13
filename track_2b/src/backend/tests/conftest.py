"""
Pytest configuration for RelayZero backend test suite.
Ensures unit tests run in offline deterministic fixture mode by default,
avoiding accidental network calls or live quota consumption during local testing.
"""

import os

# Set fixture mode before any test modules or backend code are imported
os.environ["APP_MODE"] = "fixture"

import pytest


@pytest.fixture(autouse=True)
def ensure_test_fixture_mode(monkeypatch):
    monkeypatch.setenv("APP_MODE", "fixture")
