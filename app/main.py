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

DEFAULT_TRANSACTIONS_CSV_PATH = Path("data/step3_transactions.csv")
RECENT_TRANSACTION_LIMIT = 10
DATE_ERROR_MESSAGE = "날짜는 YYYY-MM-DD 형식이어야 합니다."
TRANSACTION_HEADERS = (
    "date",
    "type",
    "category",
    "description",
    "amount",
    "memo",
)
SUMMARY_HEADERS = ("month", "income", "expense", "net")


def create_app(csv_path: Path = DEFAULT_TRANSACTIONS_CSV_PATH) -> FastAPI:
    """Create a FastAPI app for the budget web UI."""
    app = FastAPI()
    app.state.transactions_csv_path = csv_path

    @app.get("/", response_class=HTMLResponse)
    def root() -> str:
        """Return the web app landing text."""
        return "<h1>가계부 웹</h1>"

    @app.get("/transactions", response_class=HTMLResponse)
    def transactions_page() -> str:
        """Return the recent transaction list page."""
        transactions = _recent_transactions(app.state.transactions_csv_path)
        return _render_transactions_page(transactions)

    @app.get("/summary", response_class=HTMLResponse)
    def summary_page() -> str:
        """Return the monthly summary page."""
        summary = _monthly_summary(app.state.transactions_csv_path)
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
                app.state.transactions_csv_path,
                start,
                end,
                category,
            )
        except ValueError:
            return _render_error_page("검색", DATE_ERROR_MESSAGE)
        return _render_search_page(transactions)

    return app


app = create_app()


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
        return _render_message_page("거래 목록", "거래 내역이 없습니다.")
    return _render_page("거래 목록", _render_transactions_table(transactions))


def _render_summary_page(summary: dict[str, dict[str, int]]) -> str:
    """Render the monthly summary page HTML."""
    if not summary:
        return _render_message_page("월별 요약", "월별 요약 내역이 없습니다.")
    return _render_page("월별 요약", _render_summary_table(summary))


def _render_search_page(transactions: list[dict[str, Any]]) -> str:
    """Render the search page HTML."""
    if not transactions:
        return _render_message_page("검색 결과", "검색 결과가 없습니다.")
    return _render_page("검색 결과", _render_transactions_table(transactions))


def _render_error_page(title: str, message: str) -> str:
    """Render a simple error page."""
    return _render_message_page(title, message)


def _render_page(title: str, body: str) -> str:
    """Render a simple titled page."""
    return f"<h1>{escape(title)}</h1>{body}"


def _render_message_page(title: str, message: str) -> str:
    """Render a titled page with a paragraph message."""
    return _render_page(title, f"<p>{escape(message)}</p>")


def _render_transactions_table(transactions: list[dict[str, Any]]) -> str:
    """Render a transaction table."""
    rows = "".join(
        _render_transaction_row(transaction) for transaction in transactions
    )
    return _render_table(TRANSACTION_HEADERS, rows)


def _render_summary_table(summary: dict[str, dict[str, int]]) -> str:
    """Render a monthly summary table."""
    rows = "".join(
        _render_summary_row(month, totals)
        for month, totals in sorted(summary.items())
    )
    return _render_table(SUMMARY_HEADERS, rows)


def _render_table(headers: tuple[str, ...], rows: str) -> str:
    """Render a table from headers and pre-rendered rows."""
    return f"<table>{_render_header_row(headers)}{rows}</table>"


def _render_header_row(headers: tuple[str, ...]) -> str:
    """Render a table header row."""
    header_cells = "".join(f"<th>{escape(header)}</th>" for header in headers)
    return f"<tr>{header_cells}</tr>"


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
