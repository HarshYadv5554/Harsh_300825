from pathlib import Path
import sys
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.base import init_db
from app.db.session import SessionLocal
from app.models.entities import StoreStatus, BusinessHours, StoreTimezone


def add_demo_data():
    init_db()
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(StoreStatus).delete()
        db.query(BusinessHours).delete()
        db.query(StoreTimezone).delete()
        
        # Add demo stores
        stores = ["store_001", "store_002", "store_003"]
        
        # Add timezones
        for store_id in stores:
            db.add(StoreTimezone(
                store_id=store_id,
                timezone_str="America/New_York"
            ))
        
        # Add business hours (9 AM - 6 PM, Monday-Friday)
        for store_id in stores:
            for day in range(5):  # Monday to Friday
                db.add(BusinessHours(
                    store_id=store_id,
                    day_of_week=day,
                    start_time_local="09:00:00",
                    end_time_local="18:00:00"
                ))
        
        # Add status observations over the last week
        base_time = datetime.now() - timedelta(days=7)
        base_time = base_time.replace(hour=9, minute=0, second=0, microsecond=0)
        
        for store_id in stores:
            current_time = base_time
            # Generate hourly observations for 7 days
            for day in range(7):
                for hour in range(9, 18):  # 9 AM to 6 PM
                    current_time = base_time + timedelta(days=day, hours=hour)
                    
                    # Simulate some downtime (store_001 has issues on Tuesday)
                    if store_id == "store_001" and day == 1 and hour in [12, 13, 14]:
                        status = "inactive"
                    # Simulate some downtime (store_002 has issues on Thursday)
                    elif store_id == "store_002" and day == 3 and hour in [14, 15]:
                        status = "inactive"
                    # Simulate some downtime (store_003 has issues on Wednesday)
                    elif store_id == "store_003" and day == 2 and hour in [10, 11]:
                        status = "inactive"
                    else:
                        status = "active"
                    
                    db.add(StoreStatus(
                        store_id=store_id,
                        timestamp_utc=current_time,
                        status=status
                    ))
        
        db.commit()
        print(f"Added demo data for {len(stores)} stores")
        print("Business hours: 9 AM - 6 PM, Monday-Friday")
        print("Timezone: America/New_York")
        print("Simulated downtime patterns for testing")
        
    finally:
        db.close()


if __name__ == "__main__":
    add_demo_data()
