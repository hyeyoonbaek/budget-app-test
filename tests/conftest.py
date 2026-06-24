"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from budget.core import load_transactions_from_csv, monthly_summary


@pytest.fixture(scope="session")
def step3_csv_path() -> Path:
    """Return the default CSV path for web tests."""
    return Path("data/step3_transactions.csv")


@pytest.fixture(scope="session")
def step4_csv_path() -> Path:
    """Return the large CSV path for performance tests."""
    return Path("data/step4_large_transactions.csv")


@pytest.fixture(scope="session")
def step3_transactions(step3_csv_path: Path) -> list[dict[str, object]]:
    """Load step3 transactions once for the test session."""
    return load_transactions_from_csv(step3_csv_path)


@pytest.fixture(scope="session")
def step4_transactions(step4_csv_path: Path) -> list[dict[str, object]]:
    """Load step4 transactions once for the test session."""
    return load_transactions_from_csv(step4_csv_path)


@pytest.fixture(scope="session")
def step3_summary(
    step3_transactions: list[dict[str, object]],
) -> dict[str, dict[str, int]]:
    """Compute the monthly summary once for the test session."""
    return monthly_summary(step3_transactions)


@pytest.fixture
def client(step3_csv_path: Path) -> TestClient:
    """Return a fresh client for the default web app."""
    return TestClient(create_app(step3_csv_path))


@pytest.fixture
def large_client(step4_csv_path: Path) -> TestClient:
    """Return a fresh client for the large CSV web app."""
    return TestClient(create_app(step4_csv_path))


@pytest.fixture
def empty_client(tmp_path: Path) -> TestClient:
    """Return a fresh client backed by an empty CSV file."""
    empty_csv = tmp_path / "transactions.csv"
    empty_csv.write_text("", encoding="utf-8")
    return TestClient(create_app(empty_csv))
