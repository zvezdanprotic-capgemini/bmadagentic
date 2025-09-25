# For local development, create a .env file in the root of the bmad-backend directory
# and add your Azure OpenAI credentials.
# Example .env file:
# AZURE_OPENAI_API_KEY="your_api_key"
# AZURE_OPENAI_ENDPOINT="your_endpoint"
# AZURE_OPENAI_API_VERSION="2023-12-01-preview"
# AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name"

from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    """Request model for the /chat endpoint."""
    session_id: str
    message: str

class ChatResponse(BaseModel):
    """Response model for the /chat endpoint."""
    message: str
    sender: str # e.g., "user", "analyst", "orchestrator"

class AgentInfo(BaseModel):
    """Model to represent information about an agent."""
    id: str
    title: str
    when_to_use: str

class AgentsListResponse(BaseModel):
    """Response model for the /agents endpoint."""
    agents: List[AgentInfo]

class WorkflowInfo(BaseModel):
    """Model to represent information about a workflow."""
    id: str
    name: str
    description: str

class WorkflowsListResponse(BaseModel):
    """Response model for the /workflows endpoint."""
    workflows: List[WorkflowInfo]
