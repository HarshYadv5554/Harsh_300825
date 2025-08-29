from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.base import init_db
from app.db.session import SessionLocal
from app.services.ingest_service import load_zip_into_db


def main():
    init_db()
    db = SessionLocal()
    try:
        load_zip_into_db(db, "https://storage.googleapis.com/hiring-problem-statements/store-monitoring-data.zip")
        print("Ingestion complete")
    finally:
        db.close()


if __name__ == "__main__":
    main()


