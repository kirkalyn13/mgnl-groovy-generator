from unittest.mock import MagicMock
from pipeline.validator import validate_documents


def make_doc(text: str, filename: str = "test.groovy") -> MagicMock:
    doc = MagicMock()
    doc.text = text
    doc.metadata = {"file_name": filename}
    return doc


def test_passes_valid_document():
    docs = [make_doc("def session = MgnlContext.getJCRSession('website')")]
    result = validate_documents(docs)
    assert len(result) == 1


def test_filters_empty_document():
    docs = [make_doc("")]
    result = validate_documents(docs)
    assert len(result) == 0


def test_filters_short_document():
    docs = [make_doc("short")]
    result = validate_documents(docs)
    assert len(result) == 0


def test_filters_whitespace_only_document():
    docs = [make_doc("     ")]
    result = validate_documents(docs)
    assert len(result) == 0


def test_mixed_valid_and_invalid():
    docs = [
        make_doc("def session = MgnlContext.getJCRSession('website')"),
        make_doc(""),
        make_doc("def hm = MgnlContext.getHierarchyManager('dam')"),
    ]
    result = validate_documents(docs)
    assert len(result) == 2


def test_returns_empty_list_when_all_invalid():
    docs = [make_doc(""), make_doc("short")]
    result = validate_documents(docs)
    assert len(result) == 0


def test_returns_empty_list_for_no_documents():
    result = validate_documents([])
    assert len(result) == 0