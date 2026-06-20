from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database.db import create_tables
from app.api import contracts, analysis, comparison, chat, reports, dashboard

app = FastAPI(
    title="Lexora AI — Contract Intelligence Platform",
    description="Transforming Contracts into Actionable Intelligence",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(contracts.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(comparison.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Lexora AI", "version": "1.0.0"}
