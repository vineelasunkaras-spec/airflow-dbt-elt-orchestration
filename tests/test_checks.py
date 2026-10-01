from datetime import datetime, timedelta

from data_quality.checks import completeness, freshness, row_count_drift, uniqueness

ROWS = [{"id": 1, "email": "a"}, {"id": 2, "email": ""}, {"id": 2, "email": "c"}]


def test_completeness():
    assert not completeness(ROWS, "email").passed
    assert completeness(ROWS, "email", threshold=0.6).passed


def test_uniqueness():
    r = uniqueness(ROWS, "id")
    assert not r.passed and "1 duplicates" in r.detail


def test_row_count_drift():
    assert row_count_drift(100, [95, 105, 100]).passed
    assert not row_count_drift(10, [95, 105, 100]).passed


def test_freshness():
    now = datetime(2025, 1, 2)
    assert freshness(now - timedelta(hours=1), timedelta(hours=12), now).passed
    assert not freshness(now - timedelta(days=2), timedelta(hours=12), now).passed
    assert not freshness(None, timedelta(hours=1)).passed
