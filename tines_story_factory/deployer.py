"""Tines API integration for story deployment.

This module handles deployment of generated stories to Tines
via the Tines REST API.
"""
import os
from typing import Optional
import requests
from pydantic import BaseModel


class TinesAPIConfig(BaseModel):
    """Configuration for Tines API."""
    tenant_url: str
    api_key: str
    
    @property
    def base_url(self) -> str:
        return f"{self.tenant_url}/api/v1"
    
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }


class TinesStorySpec(BaseModel):
    """Tines story specification from builder."""
    name: str
    description: str
    workflow_type: str = ""
    actions: list = []
    credentials_needed: list = []


class TinesDeployer:
    """Handles deployment of stories to Tines."""
    
    def __init__(self, config: TinesAPIConfig):
        self.config = config
    
    def create_story(self, spec: TinesStorySpec) -> dict:
        """Create a new story in Tines."""
        url = f"{self.config.base_url}/stories"
        
        payload = {
            "name": spec.name,
            "description": spec.description,
            "keep_events_for": 86400  # 24 hours
        }
        
        response = requests.post(
            url,
            headers=self.config.headers(),
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}
    
    def get_stories(self) -> list:
        """Get all stories."""
        url = f"{self.config.base_url}/stories"
        
        response = requests.get(
            url,
            headers=self.config.headers()
        )
        
        if response.status_code == 200:
            return response.json().get("stories", [])
        return []
    
    def get_story(self, story_id: int) -> dict:
        """Get a specific story."""
        url = f"{self.config.base_url}/stories/{story_id}"
        
        response = requests.get(
            url,
            headers=self.config.headers()
        )
        
        if response.status_code == 200:
            return response.json()
        return {}
    
    def delete_story(self, story_id: int) -> bool:
        """Delete a story."""
        url = f"{self.config.base_url}/stories/{story_id}"
        
        response = requests.delete(
            url,
            headers=self.config.headers()
        )
        
        return response.status_code == 200
    
    def export_story_spec(self, spec: TinesStorySpec) -> dict:
        """Export story specification for manual import."""
        return {
            "name": spec.name,
            "description": spec.description,
            "workflow_type": spec.workflow_type,
            "actions": spec.actions,
            "credentials": [
                {
                    "name": cred,
                    "type": "text",
                    "description": f"Required: {cred}"
                }
                for cred in spec.credentials_needed
            ],
            "exported_by": "LangGraph Tines Story Factory",
            "exported_at": "2024-01-01T00:00:00Z"
        }


def get_config() -> Optional[TinesAPIConfig]:
    """Get Tines API configuration from environment."""
    tenant_url = os.getenv("TINES_TENANT_URL")
    api_key = os.getenv("TINES_API_KEY")
    
    if not tenant_url or not api_key:
        return None
    
    return TinesAPIConfig(
        tenant_url=tenant_url,
        api_key=api_key
    )


async def deploy_story(spec: TinesStorySpec) -> dict:
    """
    Deploy a story to Tines.
    
    Returns deployment status and details.
    """
    config = get_config()
    
    if not config:
        return {
            "status": "error",
            "message": "TINES_TENANT_URL or TINES_API_KEY not configured",
            "deployment_method": "manual_required"
        }
    
    deployer = TinesDeployer(config)
    
    # Try to create the story
    result = deployer.create_story(spec)
    
    if "error" in result:
        # API may not support direct creation
        # Return export spec for manual import
        return {
            "status": "manual_required",
            "message": "API does not support story creation directly",
            "export_spec": deployer.export_story_spec(spec),
            "instructions": "Please create the story manually in Tines UI using the exported specification"
        }
    
    return {
        "status": "success",
        "story_id": result.get("id"),
        "story_name": result.get("name"),
        "story_url": f"{config.tenant_url}/stories/{result.get('slug')}",
        "message": "Story created successfully"
    }
