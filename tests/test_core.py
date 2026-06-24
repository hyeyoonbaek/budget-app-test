"""Tests for budget.core."""

from __future__ import annotations

from pathlib import Path

from budget.core import add_transaction, load_transactions


def sample_transaction(amount: int, description: str) -> dict[str, object]:
    """Return a transaction shaped like data/step1_transactions.csv."""
    return {
        "date": "2026-01-05",
        "type": "지출" if amount < 0 else "수입",
        "category": "식비" if amount < 0 else "급여",
        "description": description,
        "amount": amount,
        "memo": "",
    }


def test_add_transaction_increases_length(tmp_path: Path) -> None:
    storage_path = tmp_path / "transactions.csv"

    before = load_transactions(storage_path)

    add_transaction(
        storage_path,
        sample_transaction(amount=-12000, description="점심식사"),
    )

    after = load_transactions(storage_path)

    assert len(after) == len(before) + 1


def test_add_transaction_saves_negative_amount(tmp_path: Path) -> None:
    storage_path = tmp_path / "transactions.csv"

    add_transaction(
        storage_path,
        sample_transaction(amount=-1500, description="지하철"),
    )

    transactions = load_transactions(storage_path)

    assert transactions[0]["amount"] == -1500


def test_add_transaction_saves_positive_amount(tmp_path: Path) -> None:
    storage_path = tmp_path / "transactions.csv"

    add_transaction(
        storage_path,
        sample_transaction(amount=3500000, description="월급"),
    )

    transactions = load_transactions(storage_path)

    assert transactions[0]["amount"] == 3500000


def test_add_transaction_accepts_empty_description(tmp_path: Path) -> None:
    storage_path = tmp_path / "transactions.csv"

    add_transaction(
        storage_path,
        sample_transaction(amount=-5800, description=""),
    )

    transactions = load_transactions(storage_path)

    assert transactions[0]["description"] == ""
