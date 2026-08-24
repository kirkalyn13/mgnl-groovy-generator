import pytest
from unittest.mock import MagicMock, patch
from services import describe


def make_message(content):
    msg = MagicMock()
    msg.content = content
    return msg


def mock_langfuse_ctx(mock_get_client):
    mock_get_client.return_value.start_as_current_observation.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_get_client.return_value.start_as_current_observation.return_value.__exit__ = MagicMock(return_value=False)


@patch("services.describe.create_agent")
@patch("services.describe.ChatOllama")
@patch("services.describe.get_client")
def test_run_describe_returns_last_message_content(mock_get_client, mock_chat_ollama, mock_create_agent):
    mock_langfuse_ctx(mock_get_client)
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "messages": [make_message("irrelevant"), make_message("This script fetches the page title.")]
    }
    mock_create_agent.return_value = mock_agent

    result = describe.run_describe("/modules/site/pages/home")

    assert result == "This script fetches the page title."


@patch("services.describe.create_agent")
@patch("services.describe.ChatOllama")
@patch("services.describe.get_client")
def test_run_describe_invokes_agent_with_script_path_in_prompt(mock_get_client, mock_chat_ollama, mock_create_agent):
    mock_langfuse_ctx(mock_get_client)
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {"messages": [make_message("ok")]}
    mock_create_agent.return_value = mock_agent

    describe.run_describe("/modules/site/pages/home")

    sent_content = mock_agent.invoke.call_args[0][0]["messages"][0]["content"]
    assert "/modules/site/pages/home" in sent_content


@patch("services.describe.create_agent")
@patch("services.describe.ChatOllama")
@patch("services.describe.get_client")
def test_run_describe_builds_agent_with_tools_and_tool_llm(mock_get_client, mock_chat_ollama, mock_create_agent):
    mock_langfuse_ctx(mock_get_client)
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {"messages": [make_message("ok")]}
    mock_create_agent.return_value = mock_agent

    describe.run_describe("/some/path")

    mock_chat_ollama.assert_called_once_with(model=describe.TOOL_LLM, temperature=0)
    mock_create_agent.assert_called_once_with(model=mock_chat_ollama.return_value, tools=describe.TOOLS)


@patch("services.describe.create_agent")
@patch("services.describe.ChatOllama")
@patch("services.describe.get_client")
@patch("services.describe.logger")
def test_run_describe_propagates_and_logs_on_exception(mock_logger, mock_get_client, mock_chat_ollama, mock_create_agent):
    mock_langfuse_ctx(mock_get_client)
    mock_agent = MagicMock()
    mock_agent.invoke.side_effect = RuntimeError("agent error")
    mock_create_agent.return_value = mock_agent

    with pytest.raises(RuntimeError, match="agent error"):
        describe.run_describe("/broken/path")

    mock_logger.error.assert_called_once()