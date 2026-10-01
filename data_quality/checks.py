"""Lightweight, dependency-free data-quality checks."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Optional, Sequence


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


def completeness(rows: Sequence[dict], column: str, threshold: float = 0.99) -> CheckResult:
    if not rows:
        return CheckResult(f"completeness:{column}", False, "no rows")
    filled = sum(1 for r in rows if r.get(column) not in (None, ""))
    ratio = filled / len(rows)
    return CheckResult(f"completeness:{column}", ratio >= threshold, f"{ratio:.2%} populated")


def uniqueness(rows: Iterable[dict], column: str) -> CheckResult:
    seen, dupes = set(), 0
    for r in rows:
        v = r.get(column)
        dupes += v in seen
        seen.add(v)
    return CheckResult(f"unique:{column}", dupes == 0, f"{dupes} duplicates")


def row_count_drift(today: int, baseline: Sequence[int], tolerance: float = 0.3) -> CheckResult:
    """Fail if today's volume deviates from the trailing average by more than `tolerance`."""
    if not baseline:
        return CheckResult("row_count_drift", True, "no baseline")
    avg = sum(baseline) / len(baseline)
    change = abs(today - avg) / avg if avg else 0.0
    return CheckResult("row_count_drift", change <= tolerance, f"{change:.1%} vs avg {avg:.0f}")


def freshness(latest: Optional[datetime], max_age: timedelta, now: Optional[datetime] = None) -> CheckResult:
    now = now or datetime.utcnow()
    if latest is None:
        return CheckResult("freshness", False, "no timestamp")
    age = now - latest
    return CheckResult("freshness", age <= max_age, f"age {age}")
