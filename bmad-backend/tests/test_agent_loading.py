import pytest
from pathlib import Path
import yaml
import textwrap

from app.agents.base_agent import load_agent_config, BMadAgent, load_all_agents
from langchain_community.chat_models.fake import FakeListChatModel
from langchain_core.messages import AIMessage

# A mock LLM for testing purposes that is a valid Runnable
class MockRunnableLLM(FakeListChatModel):
    def __init__(self, responses: list):
        super().__init__(responses=responses)

@pytest.fixture
def agents_dir(tmp_path: Path) -> Path:
    """Creates a temporary directory with mock agent files."""
    agents_path = tmp_path / "agents"
    agents_path.mkdir()

    # Analyst agent file
    (agents_path / "analyst.md").write_text(
        textwrap.dedent("""
            # analyst
            ```yaml
            agent:
              name: Mary
              id: analyst
              title: Business Analyst
              whenToUse: For analysis.
            persona:
              role: Analyst
            ```
        """)
    )

    # PM agent file
    (agents_path / "pm.md").write_text(
        textwrap.dedent("""
            # pm
            ```yaml
            agent:
              name: John
              id: pm
              title: Product Manager
              whenToUse: For product management.
            persona:
              role: PM
            ```
        """)
    )
    
    # Invalid agent file
    (agents_path / "invalid.md").write_text("This is not a valid agent file.")

    return agents_path


def test_load_agent_config_success(agents_dir: Path):
    """Tests that a valid agent config is loaded correctly."""
    analyst_path = agents_dir / "analyst.md"
    config = load_agent_config(analyst_path)

    assert config["agent"]["name"] == "Mary"
    assert config["agent"]["id"] == "analyst"
    assert "raw_content" in config
    assert config["raw_content"].strip().startswith("# analyst")


def test_load_agent_config_failure(agents_dir: Path):
    """Tests that an invalid agent config raises a ValueError."""
    invalid_path = agents_dir / "invalid.md"
    with pytest.raises(ValueError):
        load_agent_config(invalid_path)


def test_bmad_agent_creation(agents_dir: Path):
    """Tests the creation of a BMadAgent instance."""
    analyst_path = agents_dir / "analyst.md"
    config = load_agent_config(analyst_path)
    
    mock_llm = MockRunnableLLM(responses=["mock response"])

    agent = BMadAgent(agent_id="analyst", config=config, llm=mock_llm)

    assert agent.id == "analyst"
    assert agent.info.title == "Business Analyst"
    assert agent.info.when_to_use == "For analysis."
    assert agent.runnable is not None
    # Test invocation
    response = agent.invoke([])
    assert isinstance(response, AIMessage)
    assert response.content == "mock response"


def test_load_all_agents(agents_dir: Path):
    """Tests loading all agents from a directory."""
    mock_llm = MockRunnableLLM(responses=["mock response"])
    agents = load_all_agents(agents_dir, mock_llm)

    assert "analyst" in agents
    assert "pm" in agents
    assert "invalid" not in agents # Should be skipped
    assert len(agents) == 2
    assert isinstance(agents["analyst"], BMadAgent)
