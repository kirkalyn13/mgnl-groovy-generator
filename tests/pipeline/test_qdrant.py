import pytest
from pipeline.qdrant import get_collection_size


def test_ollama_returns_768():
    assert get_collection_size("ollama") == 768


def test_gemini_returns_3072():
    assert get_collection_size("gemini") == 3072


def test_unknown_mode_defaults_to_768():
    assert get_collection_size("mistral") == 768


def test_empty_string_defaults_to_768():
    assert get_collection_size("") == 768


@pytest.mark.parametrize("mode", [None, "OLLAMA", "Gemini", "ollama "])
def test_case_and_type_sensitivity(mode):
    assert get_collection_size(mode) == 768