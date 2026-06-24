"""Tests for the FastAPI app."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_root_route_returns_budget_web() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "가계부 웹" in response.text


def test_transactions_route_shows_recent_rows() -> None:
    client = TestClient(app)

    response = client.get("/transactions")

    assert response.status_code == 200
    assert "<table>" in response.text
    assert "2026-03-29" in response.text
    assert "용돈" in response.text


def test_transactions_route_shows_message_when_empty(tmp_path: Path) -> None:
    empty_csv = tmp_path / "transactions.csv"
    empty_csv.write_text("", encoding="utf-8")

    client = TestClient(app)
    client.app.dependency_overrides.clear()

    from app import main as app_main

    original_path = app_main.TRANSACTIONS_CSV_PATH
    app_main.TRANSACTIONS_CSV_PATH = empty_csv
    try:
        response = client.get("/transactions")
    finally:
        app_main.TRANSACTIONS_CSV_PATH = original_path

    assert response.status_code == 200
    assert "거래 내역이 없습니다." in response.text
