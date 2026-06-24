"""FastAPI entrypoint for the budget web app."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from budget.core import (
    filter_transactions,
    load_transactions_from_csv,
    monthly_summary,
    parse_iso_date,
)

app = FastAPI()

TRANSACTIONS_CSV_PATH = Path("data/step3_transactions.csv")
RECENT_TRANSACTION_LIMIT = 10
DATE_ERROR_MESSAGE = "날짜는 YYYY-MM-DD 형식이어야 합니다."


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    """Return the web app landing text."""
    return "<h1>가계부 웹</h1>"


@app.get("/transactions", response_class=HTMLResponse)
def transactions_page() -> str:
    """Return the recent transaction list page."""
    transactions = _recent_transactions(TRANSACTIONS_CSV_PATH)
    return _render_transactions_page(transactions)


@app.get("/summary", response_class=HTMLResponse)
def summary_page() -> str:
    """Return the monthly summary page."""
    summary = _monthly_summary(TRANSACTIONS_CSV_PATH)
    return _render_summary_page(summary)


@app.get("/search", response_class=HTMLResponse)
def search_page(
    start: str | None = None,
    end: str | None = None,
    category: str | None = None,
) -> str:
    """Return the filtered transaction list page."""
    try:
        transactions = _search_transactions(
            TRANSACTIONS_CSV_PATH,
            start,
            end,
            category,
        )
    except ValueError:
        return _render_error_page("검색", DATE_ERROR_MESSAGE)
    return _render_search_page(transactions)


def _recent_transactions(csv_path: Path) -> list[dict[str, Any]]:
    """Load the most recent transactions from the CSV file."""
    transactions = load_transactions_from_csv(csv_path)
    transactions.sort(key=_transaction_date, reverse=True)
    return transactions[:RECENT_TRANSACTION_LIMIT]


def _monthly_summary(csv_path: Path) -> dict[str, dict[str, int]]:
    """Load monthly totals from the CSV file."""
    transactions = load_transactions_from_csv(csv_path)
    return monthly_summary(transactions)


def _search_transactions(
    csv_path: Path,
    start: str | None,
    end: str | None,
    category: str | None,
) -> list[dict[str, Any]]:
    """Load and filter transactions from the CSV file."""
    transactions = load_transactions_from_csv(csv_path)
    filtered = filter_transactions(
        transactions,
        start=_optional_date(start),
        end=_optional_date(end),
        category=category,
    )
    filtered.sort(key=_transaction_date, reverse=True)
    return filtered


def _optional_date(value: str | None) -> Any:
    """Parse an optional date string."""
    if not value:
        return None
    return parse_iso_date(value)


def _transaction_date(transaction: dict[str, Any]) -> str:
    """Return the sortable transaction date."""
    return str(transaction["date"])


def _render_transactions_page(transactions: list[dict[str, Any]]) -> str:
    """Render the transactions page HTML."""
    if not transactions:
        return "<h1>거래 목록</h1><p>거래 내역이 없습니다.</p>"
    return f"<h1>거래 목록</h1>{_render_transactions_table(transactions)}"


def _render_summary_page(summary: dict[str, dict[str, int]]) -> str:
    """Render the monthly summary page HTML."""
    if not summary:
        return "<h1>월별 요약</h1><p>월별 요약 내역이 없습니다.</p>"
    return f"<h1>월별 요약</h1>{_render_summary_table(summary)}"


def _render_search_page(transactions: list[dict[str, Any]]) -> str:
    """Render the search page HTML."""
    if not transactions:
        return "<h1>검색 결과</h1><p>검색 결과가 없습니다.</p>"
    return f"<h1>검색 결과</h1>{_render_transactions_table(transactions)}"


def _render_error_page(title: str, message: str) -> str:
    """Render a simple error page."""
    return f"<h1>{escape(title)}</h1><p>{escape(message)}</p>"


def _render_transactions_table(transactions: list[dict[str, Any]]) -> str:
    """Render a transaction table."""
    rows = "".join(
        _render_transaction_row(transaction) for transaction in transactions
    )
    headers = (
        "<tr>"
        "<th>date</th>"
        "<th>type</th>"
        "<th>category</th>"
        "<th>description</th>"
        "<th>amount</th>"
        "<th>memo</th>"
        "</tr>"
    )
    return f"<table>{headers}{rows}</table>"


def _render_summary_table(summary: dict[str, dict[str, int]]) -> str:
    """Render a monthly summary table."""
    rows = "".join(
        _render_summary_row(month, totals)
        for month, totals in sorted(summary.items())
    )
    headers = (
        "<tr>"
        "<th>month</th>"
        "<th>income</th>"
        "<th>expense</th>"
        "<th>net</th>"
        "</tr>"
    )
    return f"<table>{headers}{rows}</table>"


def _render_transaction_row(transaction: dict[str, Any]) -> str:
    """Render one transaction row."""
    return (
        "<tr>"
        f"<td>{escape(str(transaction['date']))}</td>"
        f"<td>{escape(str(transaction['type']))}</td>"
        f"<td>{escape(str(transaction['category']))}</td>"
        f"<td>{escape(str(transaction['description']))}</td>"
        f"<td>{escape(str(transaction['amount']))}</td>"
        f"<td>{escape(str(transaction['memo']))}</td>"
        "</tr>"
    )


def _render_summary_row(month: str, totals: dict[str, int]) -> str:
    """Render one summary row."""
    return (
        "<tr>"
        f"<td>{escape(month)}</td>"
        f"<td>{totals['income']}</td>"
        f"<td>{totals['expense']}</td>"
        f"<td>{totals['net']}</td>"
        "</tr>"
    )


def main() -> None:
    """Run the app with uvicorn."""
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
