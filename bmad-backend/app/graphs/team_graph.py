from typing import TypedDict, Annotated, List, Union
from langchain_core.messages import BaseMessage, ToolMessage
import operator
import logging
import traceback
import re
from pathlib import Path

from langgraph.graph import StateGraph, END

from app.agents.base_agent import BMadAgent
from app.tools.task_executor import TaskExecutor


class AgentState(TypedDict):
    """
    Represents the state of the agent graph.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    sender: str
    next: str
    # Added for task execution
    task_name: str | None
    task_params: dict | None
    task_result: str | None


def create_team_graph(llm, agents: List[BMadAgent], core_resources_path: Path):
    """
    Creates the LangGraph for the multi-agent team.
    """
    agent_map = {agent.id: agent for agent in agents}
    task_executor = TaskExecutor(llm=llm, core_resources_path=core_resources_path)
    
    # The "bmad-orchestrator" is not a real agent but the router logic.
    # We can define its logic in a separate function.
    def orchestrator_node(state: AgentState):
        """
        The orchestrator node that routes to other agents or executes tools.
        """
        last_message = state["messages"][-1]
        
        # 1. Check for tool calls from an agent
        # Simple regex to find commands like "run task <task_name> with <params>"
        # In a real system, this would be more robust, likely using LLM function calling
        match = re.search(r"run task (\w+)", last_message.content, re.IGNORECASE)
        
        if match:
            task_name = match.group(1)
            # Simple parameter parsing, can be improved
            params = {} 
            if "with" in last_message.content:
                try:
                    # A very basic way to parse params like "with {'checklist':'architect-checklist.md'}"
                    param_str = last_message.content.split("with")[1].strip()
                    params = eval(param_str)
                except:
                    params = {} # Failed to parse

            return {
                "next": "task_executor",
                "task_name": task_name,
                "task_params": params
            }

        # 2. If no tool call, route to an agent
        # For now, simple routing. This can be replaced with an LLM-based router.
        # This logic decides which agent should act next.
        if state.get("sender") == "user":
             # For now, default to analyst for the initial user message.
            return {"next": "analyst"}
        else:
            # If the last message was from an agent or tool, end the turn.
            return {"next": "END"}

    def agent_node(state: AgentState, agent_id: str):
        """A generic node that invokes a specific agent."""
        
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

    def task_node(state: AgentState):
        """
        A node that executes a task using the TaskExecutor tool.
        """
        task_name = state.get("task_name")
        task_params = state.get("task_params", {})
        
        if not task_name:
            raise ValueError("Task name not provided to task_node")
            
        logging.info(f"Executing task: {task_name} with params: {task_params}")
        
        # The context for the task is the conversation history
        context = state["messages"]
        
        try:
            result = task_executor.run(task_name, context, **task_params)
            
            # The result of a tool is represented by a ToolMessage
            tool_message = ToolMessage(content=result, tool_call_id=task_name)
            
            return {
                "messages": [tool_message],
                "sender": "tool",
                "task_result": result
            }
        except Exception as e:
            logging.error(f"Error executing task {task_name}: {e}")
            logging.error(f"Error details: {traceback.format_exc()}")
            error_message = ToolMessage(content=f"Error executing task: {e}", tool_call_id=task_name)
            return {"messages": [error_message], "sender": "tool"}

    # --- Graph Definition ---
    workflow = StateGraph(AgentState)

    # Add the orchestrator node
    workflow.add_node("orchestrator", orchestrator_node)
    # Add the task execution node
    workflow.add_node("task_executor", task_node)

    # Add a node for each specialist agent
    for agent_id, agent in agent_map.items():
        workflow.add_node(agent_id, lambda state, agent_id=agent_id: agent_node(state, agent_id))

    # --- Edge Logic ---
    
    # This function will decide which node to call after an agent has acted.
    # It can route back to the orchestrator or end the turn.
    def router(state: AgentState):
        # After an agent or a tool has run, route back to the orchestrator to decide what's next
        last_sender = state.get("sender")
        if last_sender == "user":
            # Should not happen if entry point is orchestrator, but as a safeguard
            return "orchestrator"
        
        # After a tool or agent has run, let the orchestrator decide the next step
        return "orchestrator"

    # The entry point is the orchestrator
    workflow.set_entry_point("orchestrator")

    # After the orchestrator decides, it routes to the chosen agent or the task executor
    conditional_map = {agent_id: agent_id for agent_id in agent_map.keys()}
    conditional_map["task_executor"] = "task_executor"
    conditional_map["END"] = END
    
    workflow.add_conditional_edges(
        "orchestrator",
        lambda state: state["next"],
        conditional_map
    )

    # After any specialist agent has run, call the router to decide what's next.
    for agent_id in agent_map.keys():
        workflow.add_edge(agent_id, "orchestrator") 

    # After the task executor runs, route back to the orchestrator
    workflow.add_edge("task_executor", "orchestrator")

    # Compile the graph
    return workflow.compile()
