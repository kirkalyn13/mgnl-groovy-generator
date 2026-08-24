import pytest
from unittest.mock import MagicMock, patch
from services import review


def make_message(content):
    msg = MagicMock()
    msg.content = content
    return msg


def mock_langfuse_ctx(mock_get_client):
    mock_get_client.return_value.start_as_current_observation.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_get_client.return_value.start_as_current_observation.return_value.__exit__ = MagicMock(return_value=False)


@patch("services.review.create_agent")
@patch("services.review.ChatOllama")
@patch("services.review.get_client")
def test_run_review_returns_review_llm_content(mock_get_client, mock_chat_ollama, mock_create_agent):
    mock_langfuse_ctx(mock_get_client)
    mock_tool_llm, mock_review_llm = MagicMock(), MagicMock()
    mock_chat_ollama.side_effect = [mock_tool_llm, mock_review_llm]

    mock_tool_agent = MagicMock()
    mock_tool_agent.invoke.return_value = {"messages": [make_message("def foo() { ... }")]}
    mock_create_agent.return_value = mock_tool_agent

    mock_review_llm.invoke.return_value = make_message("Looks good, minor naming nits.")

    result = review.run_review("/modules/site/pages/home")

    assert result == "Looks good, minor naming nits."


@patch("services.review.create_agent")
@patch("services.review.ChatOllama")
@patch("services.review.get_client")
def test_run_review_fetches_script_before_reviewing(mock_get_client, mock_chat_ollama, mock_create_agent):
    mock_langfuse_ctx(mock_get_client)
    mock_tool_llm, mock_review_llm = MagicMock(), MagicMock()
    mock_chat_ollama.side_effect = [mock_tool_llm, mock_review_llm]

    mock_tool_agent = MagicMock()
    mock_tool_agent.invoke.return_value = {"messages": [make_message("def foo() { ... }")]}
    mock_create_agent.return_value = mock_tool_agent
    mock_review_llm.invoke.return_value = make_message("review")

    review.run_review("/modules/site/pages/home")

    fetch_prompt = mock_tool_agent.invoke.call_args[0][0]["messages"][0]["content"]
    assert "/modules/site/pages/home" in fetch_prompt

    review_prompt = mock_review_llm.invoke.call_args[0][0]
    assert "def foo() { ... }" in review_prompt


@patch("services.review.create_agent")
@patch("services.review.ChatOllama")
@patch("services.review.get_client")
def test_run_review_builds_tool_and_review_llms_with_configured_models(mock_get_client, mock_chat_ollama, mock_create_agent):
    mock_langfuse_ctx(mock_get_client)
    mock_tool_llm, mock_review_llm = MagicMock(), MagicMock()
    mock_chat_ollama.side_effect = [mock_tool_llm, mock_review_llm]

    mock_tool_agent = MagicMock()
    mock_tool_agent.invoke.return_value = {"messages": [make_message("script")]}
    mock_create_agent.return_value = mock_tool_agent
    mock_review_llm.invoke.return_value = make_message("review")

    review.run_review("/some/path")

    assert mock_chat_ollama.call_args_list[0].kwargs == {"model": review.TOOL_LLM, "temperature": 0}
    assert mock_chat_ollama.call_args_list[1].kwargs == {"model": review.REVIEW_LLM, "temperature": 0}
    mock_create_agent.assert_called_once_with(model=mock_tool_llm, tools=review.TOOLS)


@patch("services.review.create_agent")
@patch("services.review.ChatOllama")
@patch("services.review.get_client")
@patch("services.review.logger")
def test_run_review_propagates_and_logs_when_fetch_fails(mock_logger, mock_get_client, mock_chat_ollama, mock_create_agent):
    mock_langfuse_ctx(mock_get_client)
    mock_tool_llm, mock_review_llm = MagicMock(), MagicMock()
    mock_chat_ollama.side_effect = [mock_tool_llm, mock_review_llm]

    mock_tool_agent = MagicMock()
    mock_tool_agent.invoke.side_effect = RuntimeError("fetch error")
    mock_create_agent.return_value = mock_tool_agent

    with pytest.raises(RuntimeError, match="fetch error"):
        review.run_review("/broken/path")

    mock_logger.error.assert_called_once()
    mock_review_llm.invoke.assert_not_called()


@patch("services.review.create_agent")
@patch("services.review.ChatOllama")
@patch("services.review.get_client")
@patch("services.review.logger")
def test_run_review_propagates_and_logs_when_review_fails(mock_logger, mock_get_client, mock_chat_ollama, mock_create_agent):
    mock_langfuse_ctx(mock_get_client)
    mock_tool_llm, mock_review_llm = MagicMock(), MagicMock()
    mock_chat_ollama.side_effect = [mock_tool_llm, mock_review_llm]

    mock_tool_agent = MagicMock()
    mock_tool_agent.invoke.return_value = {"messages": [make_message("script")]}
    mock_create_agent.return_value = mock_tool_agent
    mock_review_llm.invoke.side_effect = RuntimeError("review error")

    with pytest.raises(RuntimeError, match="review error"):
        review.run_review("/some/path")

    mock_logger.error.assert_called_once()