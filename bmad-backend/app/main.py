from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
import traceback
from pathlib import Path

from langchain_openai import AzureChatOpenAI
from langgraph.pregel import Pregel
from fastapi import Depends

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from app.models import ChatRequest, ChatResponse, AgentsListResponse, WorkflowsListResponse
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

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, graph: Pregel = Depends(get_team_graph)):
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
        
        return ChatResponse(
            message=error_message,
            sender="system"
        )


@app.get("/agents", response_model=AgentsListResponse, summary="Get a list of available agents")
def get_agents():
    """
    Returns a list of all loaded specialist agents.
    """
    if not agents:
        return {"agents": []}
    
    agent_info_list = [agent.info for agent in agents.values()]
    return {"agents": agent_info_list}


@app.get("/workflows", response_model=WorkflowsListResponse, summary="Get a list of available workflows")
def get_workflows():
    """
    (Placeholder) Returns a list of available workflows.
    """
    # This would be loaded from the core_resources/workflows directory in a full implementation
    return {"workflows": []}


@app.delete("/session/{session_id}", summary="Clear session history")
def clear_session(session_id: str):
    """
    Clears the conversation history for a specific session.
    """
    if session_id in session_history:
        del session_history[session_id]
        return {"status": "success", "message": f"Session {session_id} history cleared"}
    return {"status": "not_found", "message": f"No history found for session {session_id}"}
