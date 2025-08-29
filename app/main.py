from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import report
from app.db.base import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="Store Monitoring API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(report.router, prefix="/api")
    return app


app = create_app()


@app.on_event("startup")
def on_startup():
    init_db()


