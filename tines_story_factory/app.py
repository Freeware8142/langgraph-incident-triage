"""Combined FastAPI app with both incident triage and Tines story factory.

This module combines:
1. LangGraph Incident Triage System (existing)
2. Tines Story Factory (new)

Run with:
    uvicorn tines_story_factory.app:app --host 0.0.0.0 --port 8080
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .main import app as tines_factory_app

# Import the main app
import sys
sys.path.insert(0, '/workspace/project')
from main import app as incident_triage_app


# Create combined app
app = FastAPI(
    title="LangGraph + Tines Story Factory",
    description="Combined service with incident triage and Tines story creation",
    version="2.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers from both apps
app.include_router(tines_factory_app, prefix="/tines-factory", tags=["Tines Story Factory"])
app.include_router(incident_triage_app, prefix="/incident-triage", tags=["Incident Triage"])


@app.get("/health")
async def health():
    """Combined health check."""
    return {
        "status": "healthy",
        "services": {
            "incident_triage": "healthy",
            "tines_story_factory": "healthy"
        }
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "LangGraph + Tines Story Factory",
        "version": "2.0.0",
        "services": {
            "incident_triage": "/incident-triage",
            "tines_story_factory": "/tines-factory"
        }
    }
