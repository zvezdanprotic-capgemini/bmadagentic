import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_openai import AzureChatOpenAI

from app.models import AgentInfo


class BMadAgent:
    """Represents a single agent in the BMad system."""

    def __init__(self, agent_id: str, config: Dict[str, Any], llm: AzureChatOpenAI):
        self.id = agent_id
        self.config = config
        self.llm = llm
        self.info = self._create_agent_info()
        self.runnable = self._create_runnable()

    def _create_agent_info(self) -> AgentInfo:
        """Creates an AgentInfo model from the agent's config."""
        agent_config = self.config.get("agent", {})
        return AgentInfo(
            id=agent_config.get("id", self.id),
            title=agent_config.get("title", "Unknown"),
            when_to_use=agent_config.get("whenToUse", "N/A"),
        )

    def _create_runnable(self) -> Runnable:
        """Creates a runnable LangChain chain for the agent."""
        system_prompt = self._construct_system_prompt()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        return prompt | self.llm

    def _construct_system_prompt(self) -> str:
        """Constructs the full system prompt from the markdown file content."""
        # The raw content of the .md file is the prompt
        raw_content = self.config.get("raw_content", "")
        # Escape curly braces that are not LangChain template variables
        # This prevents LangChain from trying to interpret {topic}, {document}, etc. as template variables
        import re
        # Find all {word} patterns and escape them as {{word}} unless they are known LangChain variables
        langchain_variables = {"messages", "input", "question", "context"}
        def escape_braces(match):
            variable = match.group(1)
            if variable in langchain_variables:
                return match.group(0)  # Keep as is for LangChain variables
            else:
                return "{{" + variable + "}}"  # Escape for literal text
        
        escaped_content = re.sub(r'\{([^}]+)\}', escape_braces, raw_content)
        return escaped_content

    def invoke(self, messages: List[Dict[str, str]]):
        """Invokes the agent's runnable chain."""
        import logging
        import traceback
        
        logging.info(f"Agent {self.id} invoked with {len(messages)} messages")
        
        try:
            logging.debug(f"Input to {self.id}: {messages[-1] if messages else 'No messages'}")
            response = self.runnable.invoke({"messages": messages})
            logging.info(f"Agent {self.id} response received, length: {len(response.content) if hasattr(response, 'content') else 'N/A'}")
            return response
        except Exception as e:
            logging.error(f"Error in agent {self.id} invoke: {e}")
            logging.error(f"Error details: {traceback.format_exc()}")
            # Re-raise the exception to be handled by the caller
            raise


def load_agent_config(file_path: Path) -> Dict[str, Any]:
    """Loads and parses an agent's .md file."""
    with open(file_path, "r") as f:
        content = f.read()

    # Extract YAML from within the ```yaml block
    match = re.search(r"```yaml\n(.*?)```", content, re.DOTALL)
    if not match:
        raise ValueError(f"Could not find YAML block in {file_path}")

    yaml_content = match.group(1)
    config = yaml.safe_load(yaml_content)
    config["raw_content"] = content  # Store the full content for the system prompt
    return config


def load_all_agents(
    agents_dir: Path, llm: AzureChatOpenAI
) -> Dict[str, BMadAgent]:
    """Loads all agents from the specified directory."""
    agents = {}
    for file_path in agents_dir.glob("*.md"):
        agent_id = file_path.stem
        if agent_id not in ["bmad-orchestrator"]: # The orchestrator is the graph itself
            try:
                config = load_agent_config(file_path)
                agents[agent_id] = BMadAgent(agent_id=agent_id, config=config, llm=llm)
            except (ValueError, yaml.YAMLError) as e:
                print(f"Warning: Could not load agent {agent_id}. Reason: {e}")
    return agents
