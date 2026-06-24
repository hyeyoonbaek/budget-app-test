"""Tests for budget.core."""

from __future__ import annotations

from pathlib import Path

from budget.core import (
    add_transaction,
    filter_by_category,
    get_balance,
    load_transactions,
    load_transactions_from_csv,
    monthly_summary,
)


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


def test_get_balance_returns_zero_for_empty_storage(tmp_path: Path) -> None:
    storage_path = tmp_path / "transactions.csv"

    assert get_balance(storage_path) == 0.0


def test_get_balance_sums_income_and_expense_amounts(tmp_path: Path) -> None:
    storage_path = tmp_path / "transactions.csv"

    add_transaction(
        storage_path,
        sample_transaction(amount=3500000, description="income"),
    )
    add_transaction(
        storage_path,
        sample_transaction(amount=-12000, description="expense"),
    )

    assert get_balance(storage_path) == 3488000


def test_get_balance_matches_step2_transactions() -> None:
    storage_path = Path("data/step2_transactions.csv")

    assert get_balance(storage_path) == 24285027


def test_filter_by_category_matches_step2_category() -> None:
    transactions = load_transactions(Path("data/step2_transactions.csv"))

    filtered = filter_by_category(transactions, "여행")

    assert len(filtered) == 6
    assert all(transaction["category"] == "여행" for transaction in filtered)


def test_filter_by_category_is_case_insensitive() -> None:
    transactions = [
        sample_transaction(amount=-12000, description="lunch"),
        {
            **sample_transaction(amount=-1500, description="metro"),
            "category": "food",
        },
    ]

    filtered = filter_by_category(transactions, "FOOD")

    assert len(filtered) == 1
    assert filtered[0]["category"] == "food"


def test_filter_by_category_returns_empty_list_for_missing_category() -> None:
    transactions = load_transactions(Path("data/step2_transactions.csv"))

    assert filter_by_category(transactions, "없는카테고리") == []


def test_filter_by_category_returns_independent_results() -> None:
    transactions = load_transactions(Path("data/step2_transactions.csv"))

    filtered = filter_by_category(transactions, "여행")
    filtered.clear()

    assert len(transactions) == 50
    assert len(filter_by_category(transactions, "여행")) == 6


def test_load_transactions_from_csv_reads_step1_file() -> None:
    transactions = load_transactions_from_csv(
        Path("data/step1_transactions.csv"),
    )

    assert len(transactions) == 10
    assert transactions[0]["amount"] == -12000
    assert isinstance(transactions[0]["amount"], int)
    assert transactions[1]["amount"] == 3500000


def test_load_transactions_from_csv_reads_large_file() -> None:
    transactions = load_transactions_from_csv(
        Path("data/step4_large_transactions.csv"),
    )

    assert len(transactions) == 5000
    assert transactions[0]["date"] == "2020-01-01"
    assert transactions[-1]["date"] == "2026-06-17"


def test_get_balance_matches_large_file() -> None:
    storage_path = Path("data/step4_large_transactions.csv")

    assert get_balance(storage_path) == 1134968783.0


def test_monthly_summary_handles_large_file() -> None:
    transactions = load_transactions_from_csv(
        Path("data/step4_large_transactions.csv"),
    )

    summary = monthly_summary(transactions)

    assert len(summary) >= 65
    assert len(summary) == 78
    assert summary["2020-01"]["income"] == 37502538
    assert summary["2020-01"]["expense"] == -11873710
    assert summary["2020-01"]["net"] == 25628828
