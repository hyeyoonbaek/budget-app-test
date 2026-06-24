"""Performance-oriented tests for large CSV data."""

from __future__ import annotations

from time import perf_counter

from fastapi.testclient import TestClient

from budget.core import filter_transactions, monthly_summary, parse_iso_date

MAX_ROUTE_SECONDS = 0.5
MAX_LOAD_SECONDS = 0.2
MAX_SUMMARY_SECONDS = 0.2
MAX_FILTER_SECONDS = 0.2


def test_large_csv_route_timings_identify_slowest_path(
    large_client: TestClient,
) -> None:
    route_timings = {
        "/transactions": _measure_route(large_client, "/transactions"),
        "/summary": _measure_route(large_client, "/summary"),
        "/search": _measure_route(
            large_client,
            "/search",
            params={
                "start": "2025-01-01",
                "end": "2025-12-31",
                "category": "식비",
            },
        ),
    }

    slowest_route = max(route_timings, key=route_timings.get)
    slowest_seconds = route_timings[slowest_route]

    assert slowest_seconds < MAX_ROUTE_SECONDS, (
        f"slowest route {slowest_route} took {slowest_seconds:.4f}s; "
        f"all route timings: {route_timings}"
    )


def test_large_csv_core_timings_help_isolate_slowdowns(
    step4_csv_path,
    step4_transactions: list[dict[str, object]],
) -> None:
    load_seconds = _measure_load(step4_csv_path)
    summary_seconds = _measure_summary(step4_transactions)
    filter_seconds = _measure_filter(step4_transactions)

    assert load_seconds < MAX_LOAD_SECONDS, (
        f"csv load took {load_seconds:.4f}s from {step4_csv_path}"
    )
    assert summary_seconds < MAX_SUMMARY_SECONDS, (
        f"monthly summary took {summary_seconds:.4f}s"
    )
    assert filter_seconds < MAX_FILTER_SECONDS, (
        f"transaction filter took {filter_seconds:.4f}s"
    )


def _measure_route(
    client: TestClient,
    path: str,
    params: dict[str, str] | None = None,
) -> float:
    """Return the elapsed time for one GET request."""
    start = perf_counter()
    response = client.get(path, params=params)
    elapsed = perf_counter() - start
    assert response.status_code == 200
    return elapsed


def _measure_load(step4_csv_path) -> float:
    """Return the elapsed time for loading the large CSV."""
    from budget.core import load_transactions_from_csv

    start = perf_counter()
    transactions = load_transactions_from_csv(step4_csv_path)
    elapsed = perf_counter() - start
    assert len(transactions) == 5000
    return elapsed


def _measure_summary(step4_transactions: list[dict[str, object]]) -> float:
    """Return the elapsed time for computing the monthly summary."""
    start = perf_counter()
    summary = monthly_summary(step4_transactions)
    elapsed = perf_counter() - start
    assert len(summary) >= 65
    return elapsed


def _measure_filter(step4_transactions: list[dict[str, object]]) -> float:
    """Return the elapsed time for filtering transactions."""
    start = perf_counter()
    filtered = filter_transactions(
        step4_transactions,
        start=parse_iso_date("2025-01-01"),
        end=parse_iso_date("2025-12-31"),
        category="식비",
    )
    elapsed = perf_counter() - start
    assert filtered
    return elapsed
