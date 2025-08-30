from pathlib import Path
import sys
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.base import init_db
from app.db.session import SessionLocal
from app.models.entities import StoreStatus, BusinessHours, StoreTimezone


def add_edge_case_demo_data():
    init_db()
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(StoreStatus).delete()
        db.query(BusinessHours).delete()
        db.query(StoreTimezone).delete()
        
        # Add demo stores with different edge cases
        stores = ["store_001", "store_002", "store_003", "store_004", "store_005"]
        
        # Store 1: Normal case (9 AM - 6 PM, Monday-Friday, America/New_York)
        db.add(StoreTimezone(store_id="store_001", timezone_str="America/New_York"))
        for day in range(5):  # Monday to Friday
            db.add(BusinessHours(
                store_id="store_001",
                day_of_week=day,
                start_time_local="09:00:00",
                end_time_local="18:00:00"
            ))
        
        # Store 2: Missing business hours (should default to 24x7)
        db.add(StoreTimezone(store_id="store_002", timezone_str="America/New_York"))
        # No business hours added - should default to 24x7
        
        # Store 3: Missing timezone (should default to America/Chicago)
        # No timezone added - should default to America/Chicago
        for day in range(5):  # Monday to Friday
            db.add(BusinessHours(
                store_id="store_003",
                day_of_week=day,
                start_time_local="09:00:00",
                end_time_local="18:00:00"
            ))
        
        # Store 4: Overnight business hours (11 PM - 7 AM)
        db.add(StoreTimezone(store_id="store_004", timezone_str="America/New_York"))
        for day in range(5):  # Monday to Friday
            db.add(BusinessHours(
                store_id="store_004",
                day_of_week=day,
                start_time_local="23:00:00",  # 11 PM
                end_time_local="07:00:00"     # 7 AM (next day)
            ))
        
        # Store 5: Sparse observations (only 2-3 per day)
        db.add(StoreTimezone(store_id="store_005", timezone_str="America/New_York"))
        for day in range(5):  # Monday to Friday
            db.add(BusinessHours(
                store_id="store_005",
                day_of_week=day,
                start_time_local="09:00:00",
                end_time_local="18:00:00"
            ))
        
        # Add status observations over the last week
        base_time = datetime.now() - timedelta(days=7)
        base_time = base_time.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Store 1: Normal hourly observations
        for day in range(7):
            for hour in range(9, 18):  # 9 AM to 6 PM
                current_time = base_time + timedelta(days=day, hours=hour)
                status = "active" if day < 5 else "inactive"  # Weekends inactive
                db.add(StoreStatus(
                    store_id="store_001",
                    timestamp_utc=current_time,
                    status=status
                ))
        
        # Store 2: 24x7 observations (every 4 hours)
        for day in range(7):
            for hour in range(0, 24, 4):  # Every 4 hours
                current_time = base_time + timedelta(days=day, hours=hour)
                status = "active" if hour in [8, 12, 16, 20] else "inactive"
                db.add(StoreStatus(
                    store_id="store_002",
                    timestamp_utc=current_time,
                    status=status
                ))
        
        # Store 3: Normal hourly observations (America/Chicago default)
        for day in range(7):
            for hour in range(9, 18):  # 9 AM to 6 PM
                current_time = base_time + timedelta(days=day, hours=hour)
                status = "active" if day < 5 else "inactive"
                db.add(StoreStatus(
                    store_id="store_003",
                    timestamp_utc=current_time,
                    status=status
                ))
        
        # Store 4: Overnight observations (11 PM - 7 AM)
        for day in range(7):
            for hour in range(23, 24):  # 11 PM
                current_time = base_time + timedelta(days=day, hours=hour)
                db.add(StoreStatus(
                    store_id="store_004",
                    timestamp_utc=current_time,
                    status="active"
                ))
            for hour in range(0, 7):  # 12 AM to 6 AM
                current_time = base_time + timedelta(days=day + 1, hours=hour)
                db.add(StoreStatus(
                    store_id="store_004",
                    timestamp_utc=current_time,
                    status="active"
                ))
        
        # Store 5: Sparse observations (only 3 per day)
        for day in range(7):
            sparse_hours = [9, 13, 17]  # Only 9 AM, 1 PM, 5 PM
            for hour in sparse_hours:
                current_time = base_time + timedelta(days=day, hours=hour)
                status = "active" if day < 5 else "inactive"
                db.add(StoreStatus(
                    store_id="store_005",
                    timestamp_utc=current_time,
                    status=status
                ))
        
        db.commit()
        print("=== EDGE CASE DEMO DATA ADDED ===")
        print("store_001: Normal case (9 AM - 6 PM, ET, hourly observations)")
        print("store_002: Missing business hours (24x7 default, every 4 hours)")
        print("store_003: Missing timezone (America/Chicago default, hourly)")
        print("store_004: Overnight business hours (11 PM - 7 AM, hourly)")
        print("store_005: Sparse observations (only 3 per day)")
        print("Business days: Monday-Friday only")
        
    finally:
        db.close()


if __name__ == "__main__":
    add_edge_case_demo_data()
