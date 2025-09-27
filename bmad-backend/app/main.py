from fastapi import FastAPI, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
import traceback
from pathlib import Path
from typing import Dict, Any

from langchain_openai import AzureChatOpenAI
from langgraph.pregel import Pregel
from fastapi import Depends

from app.security import get_current_user, is_admin

# Import services
from app.services.document_storage import DocumentStorage
from app.services.document_extractor import DocumentExtractor
from app.services.llm_response_logger import LLMResponseLogger

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from app.models import ChatRequest, ChatResponse, AgentsListResponse, WorkflowsListResponse, ManagedDocument, ManagedDocumentsResponse, CredentialsRequest, LoginRequest, RegisterRequest, AuthResponse
from app.agents.base_agent import load_all_agents, BMadAgent
from app.graphs.team_graph import create_team_graph, AgentState
from langchain_core.messages import HumanMessage, AIMessage
from typing import Any, List

# Load environment variables from .env file
dotenv_path = Path(__file__).parent.parent / '.env'
logging.info(f"Looking for .env file at: {dotenv_path}")
if dotenv_path.exists():
    logging.info(f".env file found, loading variables")
    load_dotenv(dotenv_path=dotenv_path)
else:
    logging.warning(f".env file not found at {dotenv_path}, falling back to environment variables")
    load_dotenv()

# --- Configuration ---
# It's recommended to set these in your environment or a .env file
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

logging.info("Environment variables loaded. API endpoint and deployment configured.")

CORE_RESOURCES_PATH = Path(__file__).parent / "core_resources"

# --- FastAPI App Initialization ---
app = FastAPI(
    title="BMad Agentic System",
    description="A multi-agent system based on the BMad-Method.",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Objects ---
# In a real app, you might manage these resources more carefully
llm: AzureChatOpenAI | None = None
agents: dict[str, BMadAgent] = {}
team_graph: Pregel | None = None
# Store conversation history by session ID
session_history: dict[str, list[HumanMessage | Any]] = {}
# Document storage and extraction services
document_storage = DocumentStorage()
document_extractor = DocumentExtractor()
llm_response_logger = LLMResponseLogger()
# Store credentials by session ID - simple in-memory dict for now
session_credentials: dict[str, dict[str, dict[str, str]]] = {}

def get_team_graph() -> Pregel:
    """Dependency to get the compiled team graph."""
    if team_graph is None:
        # This should not happen in a running app, but it's a safeguard
        raise RuntimeError("Team graph is not initialized.")
    return team_graph

@app.on_event("startup")
def startup_event():
    """
    Initializes the LLM and loads agents on application startup.
    """
    global llm, agents, team_graph

    try:
        # Log environment variables (masked for security)
        logging.debug(f"AZURE_OPENAI_ENDPOINT: {AZURE_OPENAI_ENDPOINT}")
        logging.debug(f"AZURE_OPENAI_DEPLOYMENT_NAME: {AZURE_OPENAI_DEPLOYMENT_NAME}")
        logging.debug(f"AZURE_OPENAI_API_VERSION: {AZURE_OPENAI_API_VERSION}")
        logging.debug(f"AZURE_OPENAI_API_KEY: {'*' * 10 + AZURE_OPENAI_API_KEY[-5:] if AZURE_OPENAI_API_KEY else 'Not set'}")
        
        if not all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_NAME]):
            logging.warning("Some Azure OpenAI environment variables are not set.")
            logging.warning("Using mock LLM for development.")
            # Create a simple mock that will work with our code
            from unittest.mock import MagicMock
            mock_llm = MagicMock()
            mock_llm.invoke.return_value.content = "This is a mock response for development."
            llm = mock_llm
        else:
            logging.info("Initializing Azure OpenAI client...")
            try:
                llm = AzureChatOpenAI(
                    api_key=AZURE_OPENAI_API_KEY,
                    azure_endpoint=AZURE_OPENAI_ENDPOINT,
                    api_version=AZURE_OPENAI_API_VERSION,
                    azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
                    max_completion_tokens=5000  # Use max_completion_tokens for newer API versions
                )
                logging.info("Azure OpenAI client initialized successfully.")
                
                # Test connection to Azure OpenAI
                logging.info("Testing Azure OpenAI connection...")
                test_result = llm.invoke("This is a test message to verify the connection.")
                logging.info(f"Connection test successful. Response type: {type(test_result)}")
            except Exception as api_error:
                logging.error(f"Error initializing Azure OpenAI client: {api_error}")
                logging.error(f"Error details: {traceback.format_exc()}")
                raise
        
        agents_path = CORE_RESOURCES_PATH / "agents"
        logging.info(f"Loading agents from {agents_path}...")
        agents = load_all_agents(agents_path, llm)
        logging.info(f"Loaded {len(agents)} agents.")

        logging.info("Creating team graph...")
        team_graph = create_team_graph(llm, list(agents.values()), CORE_RESOURCES_PATH)
        logging.info("Team graph created.")
    except Exception as e:
        logging.error(f"Error during startup: {e}")
        logging.error(f"Full traceback: {traceback.format_exc()}")
        # Continue startup even if there's an error - we'll handle specific endpoints gracefully


# --- API Endpoints ---

@app.get("/", summary="Root endpoint to check service status")
def read_root():
    """Checks if the service is running."""
    return {"status": "BMad Backend is running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, graph: Pregel = Depends(get_team_graph), current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Handles a chat message from the user, routes it through the agent graph,
    and returns the final response. Maintains conversation history by session ID.
    """
    logging.info(f"Received chat request for session {request.session_id}: {request.message[:50]}...")
    
    try:
        # Get existing session history or initialize new one
        if request.session_id not in session_history:
            session_history[request.session_id] = []
        
        # Add new user message to history
        new_user_message = HumanMessage(content=request.message)
        session_history[request.session_id].append(new_user_message)
        
        # Use full session history as input to the graph
        inputs = {"messages": session_history[request.session_id], "sender": "user"}
        logging.info(f"Invoking agent graph with {len(inputs['messages'])} messages in history...")
        
        # Add a timeout to help diagnose hanging requests
        import asyncio
        try:
            # Create a task for the graph invocation
            final_state = graph.invoke(inputs)
            logging.info("Graph invocation completed successfully")
        except Exception as graph_error:
            logging.error(f"Error during graph invocation: {graph_error}")
            logging.error(f"Error details: {traceback.format_exc()}")
            raise

        last_message = final_state["messages"][-1]
        # Add the assistant response to the session history
        session_history[request.session_id].append(last_message)
        
        # Extract documents from LLM response
        try:
            response_text = last_message.content
            extracted_docs = document_extractor.extract_documents_from_response(response_text, request.session_id)
            
            # Save extracted documents
            for doc in extracted_docs:
                document_storage.save_document(doc, request.session_id)
                
            if extracted_docs:
                logging.info(f"Extracted {len(extracted_docs)} documents from LLM response")
        except Exception as doc_error:
            logging.error(f"Error extracting documents: {doc_error}")
        
        # Log response (best effort, non-blocking on failure)
        try:
            llm_response_logger.log_response(
                session_id=request.session_id,
                content=last_message.content,
                sender=final_state.get("sender", "assistant"),
                extra={"message_index": len(session_history[request.session_id]) - 1}
            )
        except Exception as log_err:
            logging.error(f"LLM response logging failed: {log_err}")

        logging.info(f"Returning response from {final_state.get('sender', 'assistant')}")
        return ChatResponse(
            message=last_message.content,
            sender=final_state.get("sender", "assistant")
        )
    except Exception as e:
        logging.error(f"Unhandled exception in chat endpoint: {e}")
        logging.error(f"Full traceback: {traceback.format_exc()}")
        
        # Even in case of error, we still add the user message to history
        # This ensures we don't lose context even when errors occur
        if request.session_id not in session_history:
            session_history[request.session_id] = [HumanMessage(content=request.message)]
        
        # Return a graceful error response to the user
        error_message = f"I'm sorry, I encountered an error: {str(e)}. Please check the server logs for more details."
        error_ai_message = AIMessage(content=error_message)
        
        # Add error message to session history
        session_history[request.session_id].append(error_ai_message)
        
        try:
            llm_response_logger.log_response(
                session_id=request.session_id,
                content=error_message,
                sender="system",
                extra={"error": True, "exception_type": type(e).__name__}
            )
        except Exception as log_err:
            logging.error(f"Error logging failed: {log_err}")

        return ChatResponse(
            message=error_message,
            sender="system"
        )

@app.get("/api/documents", response_model=ManagedDocumentsResponse)
async def get_documents(session_id: str = None, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all managed documents, optionally filtered by session ID. Requires authentication."""
    if session_id:
        documents = document_storage.get_documents_for_session(session_id)
    else:
        documents = document_storage.get_all_documents()
    return ManagedDocumentsResponse(documents=documents)

@app.get("/api/logs/{session_id}")
async def get_session_logs(session_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Return list of log metadata for a session."""
    logs = llm_response_logger.list_logs(session_id)
    return {"session_id": session_id, "logs": logs}

@app.get("/api/logs/{session_id}/{filename}")
async def get_session_log_file(session_id: str, filename: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Return the full content of a specific log file."""
    content = llm_response_logger.read_log(session_id, filename)
    if content is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return content

@app.post("/api/credentials")
async def store_credentials(request: CredentialsRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Store service credentials for a session. Requires authentication."""
    session_id = request.session_id
    service = request.service
    
    # Initialize session if not exists
    if session_id not in session_credentials:
        session_credentials[session_id] = {}
    
    # Store credentials for this service
    session_credentials[session_id][service] = request.credentials
    
    return {"message": f"Credentials stored for {service}", "session_id": session_id}

@app.get("/api/credentials/{session_id}/{service}")
async def get_credentials(session_id: str, service: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get credentials for a specific service and session. Requires authentication."""
    if session_id not in session_credentials:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    if service not in session_credentials[session_id]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Credentials for {service} not found")
    
    return session_credentials[session_id][service]

@app.post("/api/figma/components")
async def get_figma_components(request: dict, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get components from a Figma file. Requires authentication."""
    from app.services.figma_service import FigmaService
    
    session_id = request.get("session_id")
    file_id = request.get("file_id")
    
    if not session_id or not file_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="session_id and file_id are required")
    
    # Get Figma credentials for this session
    if session_id not in session_credentials or "figma" not in session_credentials[session_id]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Figma credentials not found for this session")
    
    figma_creds = session_credentials[session_id]["figma"]
    figma_service = FigmaService(token=figma_creds["token"])
    
    # Get the documents from the Figma service
    documents = figma_service.get_file_components(file_id, session_id)
    
    # Save the documents in our document storage service
    for doc in documents:
        document_storage.save_document(doc, session_id)
    
    return {"documents": documents}

@app.post("/api/figma/user-flows")
async def get_figma_user_flows(request: dict, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user flows from a Figma file. Requires authentication."""
    from app.services.figma_service import FigmaService
    
    session_id = request.get("session_id")
    file_id = request.get("file_id")
    
    if not session_id or not file_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="session_id and file_id are required")
    
    # Get Figma credentials for this session
    if session_id not in session_credentials or "figma" not in session_credentials[session_id]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Figma credentials not found for this session")
    
    figma_creds = session_credentials[session_id]["figma"]
    figma_service = FigmaService(token=figma_creds["token"])
    
    # Get the documents from the Figma service
    documents = figma_service.get_user_flow_diagram(file_id, session_id)
    
    # Save the documents in our document storage service
    for doc in documents:
        document_storage.save_document(doc, session_id)
    
    return {"documents": documents}

@app.get("/api/agents", response_model=AgentsListResponse)
def get_agents(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns a list of all loaded agents. Requires authentication."""
    if not agents:
        return {"agents": []}
    
    agent_info_list = [agent.info for agent in agents.values()]
    return {"agents": agent_info_list}


@app.get("/api/workflows", response_model=WorkflowsListResponse, summary="Get a list of available workflows")
def get_workflows(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    (Placeholder) Returns a list of available workflows. Requires authentication.
    """
    # This would be loaded from the core_resources/workflows directory in a full implementation
    return {"workflows": []}


@app.delete("/session/{session_id}", summary="Clear session history")
def clear_session(session_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Clears the conversation history for a specific session. Requires authentication.
    """
    if session_id in session_history:
        del session_history[session_id]
        return {"status": "success", "message": f"Session {session_id} history cleared"}
    return {"status": "not_found", "message": f"No history found for session {session_id}"}

# Include routes
from app.routes.document_routes import router as document_router
from app.routes.auth_routes import router as auth_router

# Create an API router for /api endpoints
api_router = APIRouter(prefix="/api")

@api_router.get("/", summary="API root endpoint")
async def api_root():
    """API root endpoint to check API status."""
    return {"status": "BMAD API is running", "version": "1.0.0"}

app.include_router(api_router)
app.include_router(document_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
