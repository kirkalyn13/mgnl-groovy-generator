from unittest.mock import MagicMock, patch
from pipeline import loader


@patch("pipeline.loader.SimpleDirectoryReader")
def test_load_documents_uses_default_path_and_extensions(mock_reader_cls):
    mock_reader_cls.return_value.load_data.return_value = []

    loader.load_documents()

    mock_reader_cls.assert_called_once_with(loader.DEFAULT_DOCS_PATH, required_exts=loader.EXTENSIONS)


@patch("pipeline.loader.SimpleDirectoryReader")
def test_load_documents_uses_custom_path(mock_reader_cls):
    mock_reader_cls.return_value.load_data.return_value = []

    loader.load_documents("/custom/docs")

    mock_reader_cls.assert_called_once_with("/custom/docs", required_exts=loader.EXTENSIONS)


@patch("pipeline.loader.SimpleDirectoryReader")
def test_load_documents_returns_loaded_data(mock_reader_cls):
    expected_docs = [MagicMock(), MagicMock()]
    mock_reader_cls.return_value.load_data.return_value = expected_docs

    result = loader.load_documents("/custom/docs")

    assert result == expected_docs


@patch("pipeline.loader.SimpleDirectoryReader")
def test_load_documents_returns_empty_list_when_no_documents_found(mock_reader_cls):
    mock_reader_cls.return_value.load_data.return_value = []

    result = loader.load_documents("/empty/docs")

    assert result == []


@patch("pipeline.loader.SimpleDirectoryReader")
@patch("pipeline.loader.logger")
def test_load_documents_logs_loaded_count(mock_logger, mock_reader_cls):
    mock_reader_cls.return_value.load_data.return_value = [MagicMock(), MagicMock(), MagicMock()]

    loader.load_documents("/custom/docs")

    assert mock_logger.info.call_count == 2
    assert "3" in mock_logger.info.call_args_list[1][0][0]

def test_convert_to_document_maps_fields_correctly():
    data = [{"@name": "myScript.groovy", "text": "println 'hi'"}]
    result = loader.convert_to_document(data)

    assert len(result) == 1
    doc = result[0]
    assert doc.text == "println 'hi'"
    assert doc.metadata["file_name"] == "myScript.groovy"
    assert doc.metadata["script_name"] == "myScript"
    assert doc.metadata["file_type"] == ".groovy"
    assert doc.metadata["source"] == "magnolia_cms"
    assert "ingested_at" in doc.metadata


def test_convert_to_document_handles_missing_name():
    data = [{"text": "println 'no name'"}]
    result = loader.convert_to_document(data)

    assert result[0].metadata["file_name"] == ""
    assert result[0].metadata["script_name"] == ""


def test_convert_to_document_handles_missing_text():
    data = [{"@name": "empty.groovy"}]
    result = loader.convert_to_document(data)

    assert result[0].text == ""


def test_convert_to_document_handles_empty_list():
    assert loader.convert_to_document([]) == []


def test_convert_to_document_excluded_metadata_keys():
    data = [{"@name": "a.groovy", "text": "x"}]
    doc = loader.convert_to_document(data)[0]

    assert doc.excluded_embed_metadata_keys == ["ingested_at", "source"]
    assert doc.excluded_llm_metadata_keys == ["ingested_at"]


def test_convert_to_document_multiple_items():
    data = [
        {"@name": "a.groovy", "text": "x"},
        {"@name": "b.groovy", "text": "y"},
    ]
    result = loader.convert_to_document(data)

    assert len(result) == 2
    assert result[0].metadata["file_name"] == "a.groovy"
    assert result[1].metadata["file_name"] == "b.groovy"