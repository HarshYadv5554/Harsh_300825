# Store Monitoring Backend (FastAPI)

Backend service to compute per-store uptime/downtime over last hour/day/week within business hours using status pings, business hours, and timezones.

## Quickstart

1. Create and activate Python 3.11+ environment
2. Install deps: `pip install -r requirements.txt`
3. Run API: `uvicorn app.main:app --reload`
4. Ingest data (one-time or as data updates):
   - Python REPL example:
     ```python
     from app.db.base import init_db
     from app.db.session import SessionLocal
     from app.services.ingest_service import load_zip_into_db
     init_db()
     db = SessionLocal()
     load_zip_into_db(db, "https://storage.googleapis.com/hiring-problem-statements/store-monitoring-data.zip")
     db.close()
     ```
   - Windows cmd one-liner:
     ```bat
     python -c "from app.db.base import init_db; from app.db.session import SessionLocal; from app.services.ingest_service import load_zip_into_db; init_db(); db=SessionLocal(); load_zip_into_db(db, 'https://storage.googleapis.com/hiring-problem-statements/store-monitoring-data.zip'); db.close(); print('Ingestion complete')"
     ```

## Endpoints

- POST `/api/trigger_report` → returns `report_id` and starts report generation
- GET `/api/get_report?report_id=...` → returns `Running` or downloads CSV when complete

## Notes

- Current time is max `timestamp_utc` from ingested status data
- Missing business hours → assume 24x7
- Missing timezone → assume `America/Chicago`

## Improvements

- Switch background tasks to a durable queue (RQ/Celery) with retries
- Add indexes and partitioning for large datasets
- Streamed CSV generation to limit memory
- Unit tests for edge cases (overnight windows, DST transitions)

## Demo flow

1) Ingest data (one time): see Quickstart step 4 or run `python scripts/ingest.py`
2) Start API: `uvicorn app.main:app --reload`
3) Trigger report and fetch result:
   - Trigger:
     ```bash
     curl -X POST http://127.0.0.1:8000/api/trigger_report
     ```
     Response example:
     ```json
     {"report_id":"<id>","status":"Running"}
     ```
   - Poll:
     ```bash
     curl "http://127.0.0.1:8000/api/get_report?report_id=<id>" -OJ
     ```

## Sample CSV

A generated sample is saved under `reports/` after running `python scripts/generate_report.py`.


