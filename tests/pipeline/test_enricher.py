from unittest.mock import MagicMock
from pipeline.enricher import add_metadata


def make_doc(filename: str, text: str = "def session = MgnlContext.getJCRSession('website')") -> MagicMock:
    doc = MagicMock()
    doc.metadata = {"file_name": filename}
    doc.text = text
    return doc


def test_adds_file_type():
    docs = [make_doc("test.groovy")]
    result = add_metadata(docs)
    assert result[0].metadata["file_type"] == ".groovy"


def test_adds_source():
    docs = [make_doc("test.groovy")]
    result = add_metadata(docs)
    assert result[0].metadata["source"] == "magnolia_cms"


def test_adds_script_name():
    docs = [make_doc("my-script.groovy")]
    result = add_metadata(docs)
    assert result[0].metadata["script_name"] == "my-script"


def test_adds_ingested_at():
    docs = [make_doc("test.groovy")]
    result = add_metadata(docs)
    assert "ingested_at" in result[0].metadata


def test_excludes_ingested_at_from_embed():
    docs = [make_doc("test.groovy")]
    result = add_metadata(docs)
    assert "ingested_at" in result[0].excluded_embed_metadata_keys


def test_excludes_ingested_at_from_llm():
    docs = [make_doc("test.groovy")]
    result = add_metadata(docs)
    assert "ingested_at" in result[0].excluded_llm_metadata_keys


def test_handles_missing_filename():
    doc = MagicMock()
    doc.metadata = {}
    result = add_metadata([doc])
    assert result[0].metadata["script_name"] == ""


def test_returns_all_documents():
    docs = [make_doc("a.groovy"), make_doc("b.groovy"), make_doc("c.groovy")]
    result = add_metadata(docs)
    assert len(result) == 3