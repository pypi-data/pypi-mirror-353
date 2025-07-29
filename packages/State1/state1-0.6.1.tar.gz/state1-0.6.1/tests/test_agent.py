import io
import sys
import pytest
from state1 import Agent
from unittest.mock import patch, MagicMock

def test_agent_run_prints_expected_output():
    agent = Agent(
        name="Demo Agent",
        version="1.0",
        description="An example AI agent",
        context="Sample Context",
        provider="openai",
        rag=False,
        websearch=True,
        cot=True,
        ui="Template1",
        actions="Email",
        action_context="Send email to admin post session completion",
        api_key="dummy-key"
    )
    captured_output = io.StringIO()
    sys.stdout = captured_output
    agent.run()
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    assert "Agent 'Demo Agent' (v1.0) initialized." in output
    assert "Description: An example AI agent" in output
    assert "Provider: openai" in output

def test_agent_chat_openai():
    agent = Agent(
        name="Test Agent",
        version="1.0",
        description="Test",
        context="Test Context",
        provider="openai",
        api_key="$YourOpenAIKey",
        model="gpt-3.5-turbo"
    )
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Hello from OpenAI!"))]
    with patch.object(agent.client.chat.completions, 'create', return_value=mock_completion) as mock_create:
        response = agent.chat([
            {"role": "user", "content": "Hello!"}
        ])
        mock_create.assert_called_once()
        assert response == "Hello from OpenAI!"

def test_agent_chat_openrouter():
    agent = Agent(
        name="Test Agent",
        version="1.0",
        description="Test",
        context="Test Context",
        provider="openrouter",
        api_key="test-key",
        model="google/gemini-2.5-pro-preview"
    )
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Hello from OpenRouter!"))]
    with patch.object(agent.client.chat.completions, 'create', return_value=mock_completion) as mock_create:
        response = agent.chat([
            {"role": "user", "content": "Hello!"}
        ])
        mock_create.assert_called_once()
        assert response == "Hello from OpenRouter!" 