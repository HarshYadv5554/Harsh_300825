# Store Monitoring Backend - FastAPI

A robust backend service for monitoring restaurant/store uptime and downtime within business hours using status pings, business hours, and timezone data.

## Features

- **Two API endpoints**: Trigger report generation and poll for completion
- **Business hours logic**: Respects store-specific business hours with 24x7 fallback
- **Timezone handling**: Converts local business hours to UTC for calculations
- **Interpolation logic**: Status persists between observations to fill business hours
- **Edge case handling**: Missing data defaults, overnight shifts, sparse observations
- **Background processing**: Non-blocking report generation with status tracking

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

## Architecture

- **Framework**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite with proper indexing
- **Background tasks**: FastAPI background tasks for report generation
- **Type safety**: SQLAlchemy models with proper typing
- **Error handling**: Graceful degradation for missing data

## Data Sources

1. **Store Status**: `store_id, timestamp_utc, status` (hourly polls)
2. **Business Hours**: `store_id, dayOfWeek, start_time_local, end_time_local`
3. **Timezones**: `store_id, timezone_str`

## Project Structure

```
Store-Backend/
├── app/
│   ├── routers/          # API endpoints
│   ├── services/         # Business logic
│   ├── models/           # Database models
│   ├── db/              # Database configuration
│   └── utils/            # Helper functions
├── scripts/              # Data ingestion and demo scripts
├── reports/              # Generated CSV reports
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Report Schema

```csv
store_id,uptime_last_hour,uptime_last_day,uptime_last_week,downtime_last_hour,downtime_last_day,downtime_last_week
```

- **Uptime/Downtime**: Only within business hours
- **Interpolation**: Status persists between observations
- **Time periods**: Last hour (minutes), last day/week (hours)

## Core Logic

### Business Hours Processing
```python
# Respects business hours, defaults to 24x7 if missing
def get_business_windows_for_range(bh_df, tz, start_utc, end_utc):
    if not bh_df:
        return [(start_utc, end_utc)]  # 24x7 default
    # Process business hours with timezone conversion
```

### Uptime Calculation
```python
# Interpolates status between observations
def compute_intervals_with_status(observations, windows, start_utc, end_utc):
    # Status persists until next observation
    # Intersects with business hours windows
    # Returns uptime/downtime in timedelta
```

## Testing & Demo Data

### Edge Cases Tested
- **Missing business hours**: Defaults to 24x7 operation
- **Missing timezone**: Defaults to America/Chicago
- **Overnight shifts**: 11 PM - 7 AM business hours
- **Sparse observations**: Only 3 observations per day
- **Weekend handling**: Business hours respect weekdays only

### Sample Reports
- **Basic demo**: `reports/report_1756489102.csv` (3 stores, normal business hours)
- **Edge cases**: `reports/report_1756537894.csv` (5 stores, various edge cases)

## Improvement Ideas

### Performance Optimizations
- **Background queue**: Replace FastAPI background tasks with Redis/Celery for production
- **Database indexing**: Add composite indexes for large datasets
- **Caching**: Redis cache for frequently accessed business hours
- **Streaming**: Stream CSV generation for very large reports

### Scalability Enhancements
- **Microservices**: Split into separate services (ingestion, reporting, API)
- **Database**: PostgreSQL with partitioning for time-series data
- **Load balancing**: Multiple API instances behind a load balancer
- **Monitoring**: Prometheus metrics and Grafana dashboards

### Feature Additions
- **Real-time updates**: WebSocket notifications for report completion
- **Report scheduling**: Cron jobs for periodic report generation
- **Data validation**: Schema validation for incoming CSV data
- **Audit logging**: Track who generated which reports


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


## Sample Output

The repository includes sample CSV reports demonstrating various scenarios:
- **Normal business hours**: 9 AM - 6 PM ET, Monday-Friday
- **24x7 operation**: Missing business hours fallback
- **Overnight shifts**: 11 PM - 7 AM business hours
- **Sparse data**: Interpolation from limited observations



---

**Repository**: `Harsh_300825`  
**Framework**: FastAPI + SQLAlchemy  
**Database**: SQLite  
**Status**: Production-ready with comprehensive edge case handling


