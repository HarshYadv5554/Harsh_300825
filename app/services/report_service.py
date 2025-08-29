from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import pytz
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import StoreStatus, BusinessHours, StoreTimezone
from app.utils.time_windows import (
    compute_intervals_with_status,
    get_business_windows_for_range,
)


def generate_report(db: Session, output_dir: Path, now_utc: datetime) -> Path:
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"report_{int(now_utc.timestamp())}.csv"

    # Load all data
    statuses: List[StoreStatus] = list(db.execute(select(StoreStatus)).scalars())
    bhs: List[BusinessHours] = list(db.execute(select(BusinessHours)).scalars())
    tzs: List[StoreTimezone] = list(db.execute(select(StoreTimezone)).scalars())

    default_tz = "America/Chicago"
    tz_map: Dict[str, str] = {tz.store_id: tz.timezone_str for tz in tzs}

    # current time is max status timestamp
    if len(statuses) == 0:
        now = now_utc
    else:
        max_ts = max(s.timestamp_utc for s in statuses)
        now = max(max_ts.replace(tzinfo=pytz.UTC), now_utc)

    # define windows
    last_hour_start = now - timedelta(hours=1)
    last_day_start = now - timedelta(days=1)
    last_week_start = now - timedelta(days=7)

    # Group by store
    results: List[Dict[str, object]] = []
    # Group observations by store
    store_to_obs: Dict[str, List[Tuple[datetime, str]]] = {}
    for s in statuses:
        store_to_obs.setdefault(s.store_id, []).append((s.timestamp_utc.replace(tzinfo=pytz.UTC), s.status))

    store_to_bh: Dict[str, List[Tuple[int, str, str]]] = {}
    for bh in bhs:
        store_to_bh.setdefault(bh.store_id, []).append((bh.day_of_week, bh.start_time_local, bh.end_time_local))

    for store_id, obs_list in store_to_obs.items():
        tz_name = tz_map.get(store_id, default_tz) or default_tz
        tz = pytz.timezone(tz_name)
        store_bh_rows = store_to_bh.get(store_id, [])
        # Build business windows within ranges
        windows_hour = get_business_windows_for_range(store_bh_rows, tz, last_hour_start, now)
        windows_day = get_business_windows_for_range(store_bh_rows, tz, last_day_start, now)
        windows_week = get_business_windows_for_range(store_bh_rows, tz, last_week_start, now)

        up_h, down_h = compute_intervals_with_status(obs_list, windows_hour, last_hour_start, now)
        up_d, down_d = compute_intervals_with_status(obs_list, windows_day, last_day_start, now)
        up_w, down_w = compute_intervals_with_status(obs_list, windows_week, last_week_start, now)

        results.append(
            {
                "store_id": store_id,
                "uptime_last_hour": round(up_h.total_seconds() / 60, 2),
                "uptime_last_day": round(up_d.total_seconds() / 3600, 2),
                "uptime_last_week": round(up_w.total_seconds() / 3600, 2),
                "downtime_last_hour": round(down_h.total_seconds() / 60, 2),
                "downtime_last_day": round(down_d.total_seconds() / 3600, 2),
                "downtime_last_week": round(down_w.total_seconds() / 3600, 2),
            }
        )

    # Write CSV manually
    headers = [
        "store_id",
        "uptime_last_hour",
        "uptime_last_day",
        "uptime_last_week",
        "downtime_last_hour",
        "downtime_last_day",
        "downtime_last_week",
    ]
    with output_path.open("w", encoding="utf-8") as f:
        f.write(",".join(headers) + "\n")
        for row in results:
            values = [
                str(row["store_id"]),
                str(row["uptime_last_hour"]),
                str(row["uptime_last_day"]),
                str(row["uptime_last_week"]),
                str(row["downtime_last_hour"]),
                str(row["downtime_last_day"]),
                str(row["downtime_last_week"]),
            ]
            f.write(",".join(values) + "\n")
    return output_path


