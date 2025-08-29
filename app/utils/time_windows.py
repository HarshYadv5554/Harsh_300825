from __future__ import annotations

from datetime import datetime, timedelta, time
from typing import List, Sequence, Tuple

import pytz


def get_business_windows_for_range(
    bh_rows: Sequence[Tuple[int, str, str]] | None,
    tz,
    start_utc: datetime,
    end_utc: datetime,
) -> List[Tuple[datetime, datetime]]:
    windows: List[Tuple[datetime, datetime]] = []
    if not bh_rows or len(bh_rows) == 0:
        windows.append((start_utc, end_utc))
        return windows

    cursor = start_utc
    while cursor < end_utc:
        local = cursor.astimezone(tz)
        local_day = local.weekday()  # 0 Monday .. 6 Sunday
        local_date = local.date()

        for day_of_week, start_str, end_str in bh_rows:
            if day_of_week != local_day:
                continue
            s_parts = [int(p) for p in str(start_str).split(":")]
            e_parts = [int(p) for p in str(end_str).split(":")]
            start_local = tz.localize(datetime.combine(local_date, time(*s_parts)))
            end_local = tz.localize(datetime.combine(local_date, time(*e_parts)))
            if end_local <= start_local:
                end_local += timedelta(days=1)
            start_window = max(start_utc, start_local.astimezone(pytz.UTC))
            end_window = min(end_utc, end_local.astimezone(pytz.UTC))
            if start_window < end_window:
                windows.append((start_window, end_window))

        # advance to next local day start
        next_local_midnight = tz.localize(datetime.combine(local_date, time(0, 0))) + timedelta(days=1)
        cursor = next_local_midnight.astimezone(pytz.UTC)

    return windows


def compute_intervals_with_status(
    observations: List[Tuple[datetime, str]],
    windows: List[Tuple[datetime, datetime]],
    start_utc: datetime,
    end_utc: datetime,
):
    if len(observations) == 0:
        total_window = sum((w[1] - w[0] for w in windows), timedelta())
        return timedelta(0), total_window

    observations.sort(key=lambda x: x[0])
    timeline = observations.copy()

    first_time, first_status = timeline[0]
    if first_time > start_utc:
        timeline.insert(0, (start_utc, first_status))
    last_time, last_status = timeline[-1]
    if last_time < end_utc:
        timeline.append((end_utc, last_status))

    uptime = timedelta(0)
    downtime = timedelta(0)

    for (t0, s0), (t1, _s1) in zip(timeline[:-1], timeline[1:]):
        seg_start = max(t0, start_utc)
        seg_end = min(t1, end_utc)
        if seg_start >= seg_end:
            continue
        covered = timedelta(0)
        for w0, w1 in windows:
            x0 = max(seg_start, w0)
            x1 = min(seg_end, w1)
            if x0 < x1:
                covered += (x1 - x0)
        if s0 == "active":
            uptime += covered
        else:
            downtime += covered

    return uptime, downtime


