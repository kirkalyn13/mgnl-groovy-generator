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