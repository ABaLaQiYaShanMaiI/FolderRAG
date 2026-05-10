"""
Tests for the parser module.
"""
from src.parser.dispatcher import parse_file


def test_text_parser(sample_text_file):
    result = parse_file(sample_text_file)
    assert result is not None
    assert result["extract_type"] == "text"
    assert result["text"] == "Hello world"


def test_pdf_parser(sample_pdf_file):
    result = parse_file(sample_pdf_file)
    assert result is not None
    assert result["extract_type"] == "text"
    assert len(result["text"]) > 0


def test_nonexistent_file():
    result = parse_file(r"C:\nonexistent\file.txt")
    assert result is None
