"""Tests for the FastAPI app."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_root_route_returns_budget_web() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "가계부 웹" in response.text
