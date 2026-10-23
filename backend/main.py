"""
EduVerify AI — FastAPI application entry point.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router

app = FastAPI(
    title="EduVerify AI",
    description=(
        "Backend API for the EduVerify AI admissions verification system. "
        "Milestone 1: in-memory synthetic data, deterministic eligibility engine."
    ),
    version="0.1.0-milestone1",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Allow the Vite dev server (default port 5173) to reach the API.
# In production this would be restricted to the actual frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
