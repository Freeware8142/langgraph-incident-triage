"""Tines Story Factory - LangGraph Multi-Agent Orchestrator.

This module provides a LangGraph-based multi-agent system for
automatically creating Tines stories.

Architecture:
    OpenHands
        ↓
    LangGraph TinesFactory Orchestrator
        ├─ Research Agent (researches Tines API, patterns)
        ├─ Architect Agent (designs story architecture)
        ├─ Builder Agent (generates story specification)
        ├─ Tester Agent (validates the spec)
        └─ Documenter Agent (generates documentation)
        ↓
    Tines Story Specification
        ↓
    Tines API / Manual Import
        ↓
    Production Tines Story
"""
import os
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END

from .base import TinesAgentState
from .research import TinesResearchAgent
from .architect import TinesArchitectAgent
from .builder import TinesBuilderAgent
from .tester import TinesTesterAgent
from .documenter import TinesDocumenterAgent


# Initialize agents
research_agent = TinesResearchAgent()
architect_agent = TinesArchitectAgent()
builder_agent = TinesBuilderAgent()
tester_agent = TinesTesterAgent()
documenter_agent = TinesDocumenterAgent()


# Build LangGraph workflow
def create_tines_factory_graph():
    """Create the Tines Story Factory LangGraph workflow."""
    workflow = StateGraph(TinesAgentState)
    
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
graph = create_tines_factory_graph()


# Request/Response Models
class StoryRequest(BaseModel):
    """Request to create a Tines story."""
    story_requirements: str = Field(
        ..., 
        description="Description of the workflow to create"
    )
    workflow_type: str = Field(
        default="incident_triage",
        description="Type of workflow (incident_triage, m365, security, etc.)"
    )
    deployment_target: str = Field(
        default="manual",
        description="Deployment target (manual, tines_api, export)"
    )


class StoryResponse(BaseModel):
    """Response with created story specification."""
    status: str
    story_name: str
    story_spec: dict
    actions_count: int
    credentials_needed: list
    validation_passed: bool
    issues_count: int
    documentation: str
    deployment_guide: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str


# Create FastAPI app
app = FastAPI(
    title="Tines Story Factory",
    description="LangGraph multi-agent system for creating Tines stories",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="Tines Story Factory"
    )


@app.post("/create-story", response_model=StoryResponse)
async def create_story(request: StoryRequest):
    """
    Create a Tines story using the multi-agent workflow.
    
    The workflow consists of:
    1. Research: Investigate Tines API and patterns
    2. Architect: Design the story architecture
    3. Builder: Generate the story specification
    4. Tester: Validate the specification
    5. Documenter: Generate documentation
    """
    # Initialize state
    initial_state = TinesAgentState(
        story_requirements=request.story_requirements,
        workflow_type=request.workflow_type
    )
    
    try:
        # Run the workflow
        result = await graph.ainvoke(initial_state)
        
        # Check for errors
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Get validation results
        tester_results = result.get("agent_results", {}).get("tester", {})
        validation_passed = tester_results.get("validation_passed", False)
        issues_count = tester_results.get("issues_count", 0)
        
        return StoryResponse(
            status="success",
            story_name=result.story_spec.get("name", "Tines Story"),
            story_spec=result.story_spec,
            actions_count=len(result.actions_json),
            credentials_needed=result.credentials_needed,
            validation_passed=validation_passed,
            issues_count=issues_count,
            documentation=result.documentation,
            deployment_guide=result.deployment_guide
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Tines Story Factory",
        "version": "1.0.0",
        "description": "LangGraph multi-agent system for creating Tines stories",
        "docs": "/docs",
        "health": "/health",
        "create_story": "/create-story"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "tines_story_factory.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8081)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )
