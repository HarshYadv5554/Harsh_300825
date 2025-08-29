from datetime import datetime
from pathlib import Path
import sys
from pathlib import Path

import pytz

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.base import init_db
from app.db.session import SessionLocal
from app.services.report_service import generate_report


def main():
    init_db()
    db = SessionLocal()
    try:
        now = datetime.now(tz=pytz.UTC)
        out = generate_report(db, Path("reports"), now)
        print(f"Report generated: {out}")
    finally:
        db.close()


if __name__ == "__main__":
    main()


