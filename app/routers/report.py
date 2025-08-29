from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytz
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db, SessionLocal
from app.models.entities import ReportJob
from app.services.report_service import generate_report


router = APIRouter(tags=["report"])


class ReportStatus(BaseModel):
    report_id: str
    status: str


REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


def _run_report_job(report_id: str):
    db = SessionLocal()
    try:
        now = datetime.now(tz=pytz.UTC)
        csv_path = generate_report(db=db, output_dir=REPORT_DIR, now_utc=now)
        job = db.get(ReportJob, report_id)
        if job:
            job.status = "Complete"
            job.completed_at = now
            job.csv_path = str(csv_path)
            db.add(job)
            db.commit()
    except Exception:
        job = db.get(ReportJob, report_id)
        if job:
            job.status = "Failed"
            db.add(job)
            db.commit()
    finally:
        db.close()


@router.post("/trigger_report", response_model=ReportStatus)
def trigger_report(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    report_id = uuid4().hex
    job = ReportJob(id=report_id, status="Running", created_at=datetime.now(tz=pytz.UTC))
    db.add(job)
    db.commit()
    background_tasks.add_task(_run_report_job, report_id)
    return ReportStatus(report_id=report_id, status="Running")


@router.get("/get_report")
def get_report(report_id: str, db: Session = Depends(get_db)):
    job = db.get(ReportJob, report_id)
    if not job:
        raise HTTPException(status_code=404, detail="report_id not found")
    if job.status != "Complete" or not job.csv_path:
        return PlainTextResponse("Running")
    file_path = Path(job.csv_path)
    if not file_path.exists():
        raise HTTPException(status_code=500, detail="report file missing")
    return FileResponse(path=str(file_path), media_type="text/csv", filename=file_path.name)


