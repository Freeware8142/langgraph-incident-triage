"""LangGraph Incident Triage System - Main orchestrator."""
import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from agents import (
    AgentState,
    ResearchAgent,
    ArchitectAgent,
    BuilderAgent,
    TesterAgent,
    DocumenterAgent,
)


# Request/Response Models
class IncidentRequest(BaseModel):
    incident_id: str = Field(..., description="Unique incident identifier")
    incident_data: dict = Field(default_factory=dict, description="Incident details")
    type: str = Field(default="generic", description="Incident type")


class TriageResponse(BaseModel):
    incident_id: str
    status: str
    triage_result: dict
    documentation: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


# Initialize agents
research_agent = ResearchAgent()
architect_agent = ArchitectAgent()
builder_agent = BuilderAgent()
tester_agent = TesterAgent()
documenter_agent = DocumenterAgent()


# Build LangGraph workflow
def create_incident_triage_graph():
    """Create the incident triage LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # Add nodes for each agent
    workflow.add_node("research", research_agent._create_node())
    workflow.add_node("architect", architect_agent._create_node())
    workflow.add_node("builder", builder_agent._create_node())
    workflow.add_node("tester", tester_agent._create_node())
    workflow.add_node("documenter", documenter_agent._create_node())

    # Define workflow edges
    workflow.set_entry_point("research")
    workflow.add_edge("research", "architect")
    workflow.add_edge("architect", "builder")
    workflow.add_edge("builder", "tester")
    workflow.add_edge("tester", "documenter")
    workflow.add_edge("documenter", END)

    return workflow.compile()


# Initialize graph
graph = create_incident_triage_graph()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting Incident Triage System")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    yield
    # Shutdown
    print("Shutting down Incident Triage System")


# Create FastAPI app
app = FastAPI(
    title="LangGraph Incident Triage System",
    description="Multi-agent incident triage system for automated incident response",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring and load balancer probes."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "development")
    )


# Readiness check endpoint
@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes/Cloud Run."""
    # Add any dependency checks here (e.g., database, external APIs)
    return {"status": "ready"}


# Triage endpoint
@app.post("/triage", response_model=TriageResponse)
async def triage_incident(request: IncidentRequest):
    """
    Process an incident through the triage workflow.
    
    The workflow consists of:
    1. Research: Gather context from Microsoft Graph and Tines
    2. Architect: Analyze patterns and determine resolution strategy
    3. Builder: Generate remediation scripts
    4. Tester: Validate remediation scripts
    5. Documenter: Generate incident report
    """
    initial_state = AgentState(
        incident_id=request.incident_id,
        incident_data=request.incident_data,
        triage_result=None,
        research_data=None,
        analysis=None,
        recommendation=None,
        build_output=None,
        test_results=None,
        documentation=None,
        error=None,
    )

    try:
        result = await graph.ainvoke(initial_state)

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        triage_result = {
            "incident_id": result["incident_id"],
            "research": result.get("research_data"),
            "analysis": result.get("analysis"),
            "recommendation": result.get("recommendation"),
            "remediation_script": result.get("build_output"),
            "test_results": result.get("test_results"),
        }

        return TriageResponse(
            incident_id=result["incident_id"],
            status=result.get("test_results", {}).get("overall_status", "UNKNOWN"),
            triage_result=triage_result,
            documentation=result.get("documentation"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Batch triage endpoint for multiple incidents
@app.post("/triage/batch")
async def triage_batch(requests: list[IncidentRequest]):
    """Process multiple incidents in batch."""
    results = []
    for req in requests:
        try:
            result = await triage_incident(req)
            results.append(result)
        except Exception as e:
            results.append({
                "incident_id": req.incident_id,
                "status": "error",
                "error": str(e)
            })
    return {"results": results}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "LangGraph Incident Triage System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        reload=os.getenv("ENVIRONMENT") == "development",
    )
