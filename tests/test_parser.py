"""
Tests for the parser module.
"""
from src.parser.dispatcher import parse_file


def test_text_parser(sample_text_file, mock_config):
    config = mock_config
    result = parse_file(sample_text_file, config)
    assert result is not None
    assert result["extract_type"] == "text"
    assert result["text"] == "Hello world"


def test_binary_parser(sample_binary_file, mock_config):
    config = mock_config
    result = parse_file(sample_binary_file, config)
    assert result is not None
    assert result["extract_type"] == "binary"
    # ASCII segments "Hello" and "World" should be extracted if length >=4
    assert "Hello" in result["text"] or "World" in result["text"]
