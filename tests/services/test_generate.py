import json
from unittest.mock import MagicMock, patch
from services import generate

def mock_langfuse_ctx(mock_get_client):
    mock_get_client.return_value.start_as_current_observation.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_get_client.return_value.start_as_current_observation.return_value.__exit__ = MagicMock(return_value=False)

# --- clean_script ---

def test_clean_script_removes_groovy_fence():
    raw = "```groovy\ndef session = MgnlContext.getJCRSession('website')\n```"
    assert "```" not in generate.clean_script(raw)


def test_clean_script_removes_plain_fence():
    raw = "```\ndef session = MgnlContext.getJCRSession('website')\n```"
    assert "```" not in generate.clean_script(raw)


def test_clean_script_strips_whitespace():
    raw = "  \ndef session = MgnlContext.getJCRSession('website')\n  "
    assert generate.clean_script(raw) == "def session = MgnlContext.getJCRSession('website')"


def test_clean_script_returns_unchanged_if_no_fence():
    raw = "def session = MgnlContext.getJCRSession('website')"
    assert generate.clean_script(raw) == raw


# --- validate_request ---

def make_llm(response: dict) -> MagicMock:
    llm = MagicMock()
    llm.complete.return_value = json.dumps(response)
    return llm


@patch("services.generate.get_client")
def test_validate_request_groovy_read_only(mock_get_client):
    mock_langfuse_ctx(mock_get_client)
    mock_get_client.return_value.__enter__ = MagicMock(return_value=MagicMock())

    llm = make_llm({"is_groovy_request": True, "is_read_only": True, "reason": "valid"})
    result = generate.validate_request("fetch all assets", llm)
    assert result["is_groovy_request"] == True
    assert result["is_read_only"] == True


@patch("services.generate.get_client")
def test_validate_request_non_groovy(mock_get_client):
    mock_langfuse_ctx(mock_get_client)

    llm = make_llm({"is_groovy_request": False, "is_read_only": True, "reason": "not groovy"})
    result = generate.validate_request("tell me a joke", llm)
    assert result["is_groovy_request"] == False


# --- generate_script ---

@patch("services.generate.get_client")
def test_generate_script_returns_valid(mock_get_client):
    mock_langfuse_ctx(mock_get_client)

    expected = {
        "script": "def session = MgnlContext.getJCRSession('website')",
        "is_valid_groovy": True,
        "is_safe": True,
    }
    llm = MagicMock()
    llm.complete.return_value = json.dumps(expected)

    result = generate.generate_script("fetch pages", [], [], "context", llm)
    assert result["is_valid_groovy"] == True
    assert result["is_safe"] == True
    assert "session" in result["script"]


@patch("services.generate.get_client")
def test_generate_script_with_workspaces_and_properties(mock_get_client):
    mock_langfuse_ctx(mock_get_client)

    expected = {
        "script": "def session = MgnlContext.getJCRSession('dam')",
        "is_valid_groovy": True,
        "is_safe": True,
    }
    llm = MagicMock()
    llm.complete.return_value = json.dumps(expected)

    result = generate.generate_script("fetch assets", ["dam"], ["title", "path"], "context", llm)
    assert result["is_valid_groovy"] == True