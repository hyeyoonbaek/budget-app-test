"""Core domain logic for the budget CLI app."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

FIELDNAMES = ["date", "type", "category", "description", "amount", "memo"]


def add_transaction(storage_path: Path, transaction: dict[str, Any]) -> None:
    """Add one transaction record to the storage.

    Args:
        storage_path: Path to the CSV storage file.
        transaction: Transaction data to append.
    """
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = storage_path.exists() and storage_path.stat().st_size > 0

    with storage_path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow({field: transaction[field] for field in FIELDNAMES})


def load_transactions(storage_path: Path) -> list[dict[str, Any]]:
    """Load all transactions from the storage file.

    Args:
        storage_path: Path to the CSV storage file.

    Returns:
        A list of transaction records.
    """
    return load_transactions_from_csv(storage_path)


def load_transactions_from_csv(csv_path: Path) -> list[dict[str, Any]]:
    """Load transactions from a CSV file.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        A list of transaction records.
    """
    if not csv_path.exists():
        return []

    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        return [_parse_transaction(row) for row in csv.DictReader(csv_file)]


def list_transactions(storage_path: Path) -> list[dict[str, Any]]:
    """Return transactions currently stored in the CSV file.

    Args:
        storage_path: Path to the CSV storage file.

    Returns:
        A list of transaction records.
    """
    return load_transactions(storage_path)


def get_balance(storage_path: Path) -> float:
    """Return the sum of income and expense amounts.

    Args:
        storage_path: Path to the CSV storage file.

    Returns:
        The total balance from all transaction amounts.
    """
    transactions = load_transactions(storage_path)
    return float(sum(transaction["amount"] for transaction in transactions))


def filter_by_category(
    transactions: list[dict[str, Any]],
    category: str,
) -> list[dict[str, Any]]:
    """Return transactions matching the category, ignoring case.

    Args:
        transactions: Transaction records to filter.
        category: Category name to match.

    Returns:
        A new list containing matching transaction records.
    """
    normalized_category = category.casefold()
    return [
        transaction
        for transaction in transactions
        if str(transaction["category"]).casefold() == normalized_category
    ]


def monthly_summary(
    transactions: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    """Return monthly income, expense, and net totals.

    Args:
        transactions: Transaction records to summarize.

    Returns:
        A mapping of YYYY-MM to income, expense, and net totals.
    """
    summary: dict[str, dict[str, int]] = {}

    for transaction in transactions:
        _update_month_summary(summary, transaction)

    return summary


def _update_month_summary(
    summary: dict[str, dict[str, int]],
    transaction: dict[str, Any],
) -> None:
    """Add one transaction into the monthly summary bucket."""
    month = _get_transaction_month(transaction)
    month_summary = summary.setdefault(month, _empty_month_summary())
    amount = int(transaction["amount"])
    month_summary["income"] += max(amount, 0)
    month_summary["expense"] += min(amount, 0)
    month_summary["net"] += amount


def _get_transaction_month(transaction: dict[str, Any]) -> str:
    """Return the YYYY-MM month key for a transaction."""
    return str(transaction["date"])[:7]


def _empty_month_summary() -> dict[str, int]:
    """Return a fresh monthly summary bucket."""
    return {"income": 0, "expense": 0, "net": 0}


def _parse_transaction(row: dict[str, str]) -> dict[str, Any]:
    """Convert a CSV row into the transaction dictionary shape."""
    transaction: dict[str, Any] = {field: row[field] for field in FIELDNAMES}
    transaction["amount"] = int(transaction["amount"])
    return transaction
