# For local development, create a .env file in the root of the bmad-backend directory
# and add your Azure OpenAI credentials.
# Example .env file:
# AZURE_OPENAI_API_KEY="your_api_key"
# AZURE_OPENAI_ENDPOINT="your_endpoint"
# AZURE_OPENAI_API_VERSION="2023-12-01-preview"
# AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name"

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

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

class ManagedDocument(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    type: str  # e.g., "Figma Design", "Jira Story", "Architecture Document"
    source: str # e.g., "FigmaService", "TaskExecutor"
    external_url: Optional[str] = None
    local_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}

class ManagedDocumentsResponse(BaseModel):
    documents: List[ManagedDocument]

class FigmaCredentials(BaseModel):
    api_token: str
    file_key: str

class CredentialsRequest(BaseModel):
    session_id: str
    service: str  # e.g., "figma", "jira", "github"
    credentials: Dict[str, str]  # flexible credential storage

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

# Authentication models
class User(BaseModel):
    id: str
    username: str
    name: str
    email: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str
    email: Optional[str] = None

class AuthResponse(BaseModel):
    user: User
    token: str
    success: bool
    message: Optional[str] = None
