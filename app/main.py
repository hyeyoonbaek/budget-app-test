"""FastAPI entrypoint for the budget web app."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from budget.core import load_transactions_from_csv

app = FastAPI()

TRANSACTIONS_CSV_PATH = Path("data/step3_transactions.csv")
RECENT_TRANSACTION_LIMIT = 10


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    """Return the web app landing text."""
    return "<h1>가계부 웹</h1>"


@app.get("/transactions", response_class=HTMLResponse)
def transactions_page() -> str:
    """Return the recent transaction list page."""
    transactions = _recent_transactions(TRANSACTIONS_CSV_PATH)
    return _render_transactions_page(transactions)


def _recent_transactions(csv_path: Path) -> list[dict[str, Any]]:
    """Load the most recent transactions from the CSV file."""
    transactions = load_transactions_from_csv(csv_path)
    transactions.sort(key=_transaction_date, reverse=True)
    return transactions[:RECENT_TRANSACTION_LIMIT]


def _transaction_date(transaction: dict[str, Any]) -> str:
    """Return the sortable transaction date."""
    return str(transaction["date"])


def _render_transactions_page(transactions: list[dict[str, Any]]) -> str:
    """Render the transactions page HTML."""
    if not transactions:
        return "<h1>거래 목록</h1><p>거래 내역이 없습니다.</p>"
    return f"<h1>거래 목록</h1>{_render_transactions_table(transactions)}"


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


def main() -> None:
    """Run the app with uvicorn."""
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
