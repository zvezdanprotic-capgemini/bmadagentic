import logging
from pathlib import Path
from typing import Any, List
from langchain_core.messages import BaseMessage
from langchain_openai import AzureChatOpenAI

class TaskExecutor:
    """
    A class to execute tasks defined in markdown files.
    """
    def __init__(self, llm: AzureChatOpenAI, core_resources_path: Path):
        self.llm = llm
        self.tasks_path = core_resources_path / "tasks"

    def _load_task_prompt(self, task_name: str) -> str:
        """Loads the prompt for a given task from its markdown file."""
        task_file = self.tasks_path / f"{task_name}.md"
        if not task_file.exists():
            raise FileNotFoundError(f"Task file not found: {task_file}")
        
        with open(task_file, "r") as f:
            return f.read()

    def run(self, task_name: str, context: List[BaseMessage], **kwargs) -> str:
        """
        Runs a task by generating a response from the LLM based on the task's prompt.
        
        Args:
            task_name: The name of the task to run (e.g., 'execute-checklist').
            context: The conversation history to provide as context to the task.
            **kwargs: Additional parameters to pass to the task prompt.
        
        Returns:
            The result of the task execution as a string.
        """
        logging.info(f"Running task '{task_name}' with params: {kwargs}")
        
        task_prompt_template = self._load_task_prompt(task_name)
        
        # Simple parameter substitution
        # In a real system, you might use a more sophisticated templating engine
        for key, value in kwargs.items():
            task_prompt_template = task_prompt_template.replace(f"{{{key}}}", str(value))
            
        # The full prompt for the task includes the task instructions and the conversation context
        full_prompt = f"{task_prompt_template}\n\n--- CONVERSATION CONTEXT ---\n"
        for msg in context:
            full_prompt += f"{msg.type}: {msg.content}\n"
        
        # For now, we'll just use a simple invocation.
        # This could be a more complex chain or runnable in the future.
        from langchain_core.prompts import ChatPromptTemplate
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", full_prompt),
            ("human", "Based on the task instructions and the conversation context, what is the next step or the final result?"),
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({})
        
        logging.info(f"Task '{task_name}' completed.")
        return response.content
