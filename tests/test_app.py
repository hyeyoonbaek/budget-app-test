"""Tests for the FastAPI app."""

from __future__ import annotations

from pathlib import Path

import pytest
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


def test_transactions_route_shows_message_when_empty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    empty_csv = tmp_path / "transactions.csv"
    empty_csv.write_text("", encoding="utf-8")

    from app import main as app_main

    monkeypatch.setattr(app_main, "TRANSACTIONS_CSV_PATH", empty_csv)

    client = TestClient(app)
    response = client.get("/transactions")

    assert response.status_code == 200
    assert "거래 내역이 없습니다." in response.text


def test_summary_route_shows_monthly_summary() -> None:
    client = TestClient(app)

    response = client.get("/summary")

    assert response.status_code == 200
    assert "<table>" in response.text
    assert "2025-02" in response.text
    assert "12940804" in response.text
    assert "-1832242" in response.text
    assert "11108562" in response.text


def test_summary_route_shows_message_when_empty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    empty_csv = tmp_path / "transactions.csv"
    empty_csv.write_text("", encoding="utf-8")

    from app import main as app_main

    monkeypatch.setattr(app_main, "TRANSACTIONS_CSV_PATH", empty_csv)

    client = TestClient(app)
    response = client.get("/summary")

    assert response.status_code == 200
    assert "월별 요약 내역이 없습니다." in response.text


def test_search_route_returns_all_when_no_filters() -> None:
    client = TestClient(app)

    response = client.get("/search")

    assert response.status_code == 200
    assert "<table>" in response.text
    assert "2025-01-02" in response.text
    assert "2026-03-29" in response.text


def test_search_route_filters_by_date_range_and_category() -> None:
    client = TestClient(app)

    response = client.get(
        "/search",
        params={"start": "2025-01-01", "end": "2025-01-31", "category": "식비"},
    )

    assert response.status_code == 200
    assert "2025-01-10" in response.text
    assert "점심식사" in response.text
    assert "환급금" not in response.text


def test_search_route_returns_friendly_error_for_bad_date() -> None:
    client = TestClient(app)

    response = client.get("/search", params={"start": "2025/01/01"})

    assert response.status_code == 200
    assert "날짜는 YYYY-MM-DD 형식이어야 합니다." in response.text
