from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime


class Base(DeclarativeBase):
    pass


class StoreStatus(Base):
    __tablename__ = "store_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(String, index=True)
    timestamp_utc: Mapped[DateTime] = mapped_column(DateTime, index=True)
    status: Mapped[str] = mapped_column(String)  # 'active' or 'inactive'


class BusinessHours(Base):
    __tablename__ = "business_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(String, index=True)
    day_of_week: Mapped[int] = mapped_column(Integer)  # 0 Monday .. 6 Sunday
    start_time_local: Mapped[str] = mapped_column(String)  # HH:MM:SS
    end_time_local: Mapped[str] = mapped_column(String)  # HH:MM:SS


class StoreTimezone(Base):
    __tablename__ = "store_timezone"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(String, index=True)
    timezone_str: Mapped[str] = mapped_column(String)


class ReportJob(Base):
    __tablename__ = "report_job"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String, index=True)  # Running | Complete | Failed
    created_at: Mapped[DateTime] = mapped_column(DateTime)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    csv_path: Mapped[str | None] = mapped_column(String, nullable=True)


