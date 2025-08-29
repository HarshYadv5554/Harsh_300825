from __future__ import annotations

import io
import zipfile
from datetime import datetime
import csv
from pathlib import Path
from typing import Optional

import requests
from sqlalchemy.orm import Session

from app.models.entities import BusinessHours, StoreStatus, StoreTimezone


def _find_csv(zip_bytes: bytes, expected_name_contains: str) -> Optional[bytes]:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in zf.namelist():
            if expected_name_contains in name and name.lower().endswith(".csv"):
                return zf.read(name)
    return None


def load_zip_into_db(db: Session, source: str) -> None:
    # source can be URL or file path
    if source.startswith("http://") or source.startswith("https://"):
        resp = requests.get(source, timeout=60)
        resp.raise_for_status()
        zip_bytes = resp.content
    else:
        zip_bytes = Path(source).read_bytes()

    status_bytes = _find_csv(zip_bytes, "store_status")
    bh_bytes = _find_csv(zip_bytes, "business_hours")
    tz_bytes = _find_csv(zip_bytes, "store_timezone")

    # Ingest timezone
    if tz_bytes:
        text = tz_bytes.decode("utf-8").splitlines()
        reader = csv.DictReader(text)
        for row in reader:
            store_id = str(row.get("store_id", "")).strip()
            timezone_str = (row.get("timezone_str") or row.get("timezone") or "").strip()
            if not store_id:
                continue
            db.add(StoreTimezone(store_id=store_id, timezone_str=timezone_str))
        db.commit()

    # Ingest business hours
    if bh_bytes:
        text = bh_bytes.decode("utf-8").splitlines()
        reader = csv.DictReader(text)
        for row in reader:
            store_id = str(row.get("store_id", "")).strip()
            day_str = str(row.get("day") or row.get("day_of_week") or "").strip()
            start_time_local = str(row.get("start_time_local", "")).strip()
            end_time_local = str(row.get("end_time_local", "")).strip()
            if not store_id or day_str == "":
                continue
            db.add(
                BusinessHours(
                    store_id=store_id,
                    day_of_week=int(day_str),
                    start_time_local=start_time_local,
                    end_time_local=end_time_local,
                )
            )
        db.commit()

    # Ingest status
    if status_bytes:
        text = status_bytes.decode("utf-8").splitlines()
        reader = csv.DictReader(text)
        for row in reader:
            store_id = str(row.get("store_id", "")).strip()
            ts_str = str(row.get("timestamp_utc", "")).strip()
            status = str(row.get("status", "")).strip().lower()
            if not store_id or not ts_str:
                continue
            # Try multiple timestamp formats
            dt = None
            for fmt in ("%Y-%m-%d %H:%M:%S %Z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z"):
                try:
                    if fmt.endswith("%z"):
                        dt = datetime.strptime(ts_str.replace("Z", "+0000"), fmt)
                    else:
                        dt = datetime.strptime(ts_str.replace("UTC", "" ).strip(), fmt)
                    break
                except Exception:
                    continue
            if dt is None:
                try:
                    dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                except Exception:
                    continue
            dt = dt.replace(tzinfo=None)
            db.add(
                StoreStatus(
                    store_id=store_id,
                    timestamp_utc=dt,
                    status=status,
                )
            )
        db.commit()


