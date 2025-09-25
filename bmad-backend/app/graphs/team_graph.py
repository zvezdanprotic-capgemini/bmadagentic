from typing import TypedDict, Annotated, List, Union
from langchain_core.messages import BaseMessage
import operator

from langgraph.graph import StateGraph, END

from app.agents.base_agent import BMadAgent


class AgentState(TypedDict):
    """
    Represents the state of the agent graph.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    sender: str
    next: str


def create_team_graph(llm, agents: List[BMadAgent]):
    """
    Creates the LangGraph for the multi-agent team.
    """
    agent_map = {agent.id: agent for agent in agents}
    
    # The "bmad-orchestrator" is not a real agent but the router logic.
    # We can define its logic in a separate function.
    def orchestrator_node(state: AgentState):
        # For now, a simple router. This will be expanded.
        # This logic will decide which agent should act next.
        # Based on the user message, it could be 'analyst', 'pm', etc.
        # Let's default to 'analyst' for the initial implementation.
        return {
            "next": "analyst"
        }

    def agent_node(state: AgentState, agent_id: str):
        """A generic node that invokes a specific agent."""
        import logging
        import traceback
        
        logging.info(f"Executing node for agent: {agent_id}")
        
        agent = agent_map.get(agent_id)
        if not agent:
            logging.error(f"Agent '{agent_id}' not found in agent_map")
            raise ValueError(f"Agent '{agent_id}' not found.")
        
        try:
            logging.info(f"Invoking agent {agent_id} with {len(state['messages'])} messages")
            result = agent.invoke(state["messages"])
            logging.info(f"Agent {agent_id} returned result successfully")
            
            return {
                "messages": [result],
                "sender": agent_id,
            }
        except Exception as e:
            logging.error(f"Error invoking agent {agent_id}: {e}")
            logging.error(f"Error details: {traceback.format_exc()}")
            # Re-raise to be handled by the graph
            raise

    # --- Graph Definition ---
    workflow = StateGraph(AgentState)

    # Add the orchestrator node
    workflow.add_node("orchestrator", orchestrator_node)

    # Add a node for each specialist agent
    for agent_id, agent in agent_map.items():
        workflow.add_node(agent_id, lambda state, agent_id=agent_id: agent_node(state, agent_id))

    # --- Edge Logic ---
    
    # This function will decide which node to call after an agent has acted.
    # It can route back to the orchestrator or end the turn.
    def router(state: AgentState):
        # For now, after any agent acts, we'll just end the turn.
        # In a real workflow, it might go back to the orchestrator or another agent.
        return END

    # The entry point is the orchestrator
    workflow.set_entry_point("orchestrator")

    # After the orchestrator decides, it routes to the chosen agent
    # This conditional routing is a key feature of LangGraph.
    conditional_map = {agent_id: agent_id for agent_id in agent_map.keys()}
    workflow.add_conditional_edges(
        "orchestrator",
        lambda state: state["next"],
        conditional_map
    )

    # After any specialist agent has run, call the router to decide what's next.
    for agent_id in agent_map.keys():
        workflow.add_edge(agent_id, END) # Simplified: agent -> END

    # Compile the graph
    return workflow.compile()
