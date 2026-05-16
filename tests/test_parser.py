"""
Tests for the parser module.
"""
import os
import tempfile
import pytest
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


def test_nonexistent_file():
    nonexistent = os.path.join(tempfile.gettempdir(), "folderrag_nonexistent_file.txt")
    result = parse_file(nonexistent)
    assert result is None


# Constants Integration Tests

try:
    from src.constants import SUPPORTED_TEXT_EXTS
    _HAS_CONSTANTS = True
except ImportError:
    _HAS_CONSTANTS = False


def _get_supported_text_extensions() -> set:
    """Get the set of supported text extensions for testing.

    Returns only pure text/parsable extensions (not Office/PDF which need special handling).
    """
    if not _HAS_CONSTANTS:
        pytest.skip("src.constants not available")

    skip_exts = {'.pdf', '.docx', '.pptx', '.xlsx'}

    pure_text_exts = set()
    for ext in sorted(SUPPORTED_TEXT_EXTS):
        if ext not in skip_exts:
            pure_text_exts.add(ext)

    return pure_text_exts


def test_constants_integration_imports():
    """Verify that constants module provides SUPPORTED_TEXT_EXTS correctly."""
    if not _HAS_CONSTANTS:
        pytest.skip("src.constants not available")

    from src.constants import SUPPORTED_TEXT_EXTS as exts
    assert len(exts) > 50, f"Expected many supported extensions, got {len(exts)}"
    assert '.txt' in exts
    assert '.py' in exts
    assert '.cs' in exts
    assert '.xaml' in exts
    assert '.md' in exts


@pytest.mark.parametrize("ext", sorted(
    _get_supported_text_extensions() if _HAS_CONSTANTS else ['.txt', '.py', '.cs', '.xaml', '.json']
))
def test_all_text_extensions_parseable(tmp_path, ext):
    """Verify dispatcher can recognize and parse files with ALL supported text extensions.

    Creates a minimal file for each extension and checks that parse_file returns valid content.
    This ensures no supported extension is accidentally dropped when constants change.
    """
    if not _HAS_CONSTANTS:
        pytest.skip("src.constants not available")

    fname = f"test{ext}"
    filepath = os.path.join(str(tmp_path), fname)

    content = "hello world test content 42"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    result = parse_file(filepath)
    assert result is not None, f"parse_file returned None for extension {ext} ({fname})"
    assert result.get("text", "").strip() == content, (
        f"Content mismatch for extension {ext}: got {result.get('text', '')!r}"
    )


def test_magic_fallback(tmp_path, monkeypatch):
    """Verify is_file_supported falls back to extension-based detection when magic.Magic fails.

    This test simulates the scenario where python-magic is installed but raises an exception
    when from_file() is called, ensuring the fallback to extension-based detection works.
    """
    from src.gui_scanner import is_file_supported

    # Create test files with various extensions
    test_files = {
        '.py': 'print("hello")\n',
        '.txt': 'hello world\n',
        '.pdf': b'%PDF-1.4\nfake pdf content\n',
    }

    for ext, content in test_files.items():
        fpath = os.path.join(str(tmp_path), f'test{ext}')
        mode = 'wb' if isinstance(content, bytes) else 'w'
        encoding = None if isinstance(content, bytes) else 'utf-8'
        with open(fpath, mode, encoding=encoding) as f:
            f.write(content)

        # Without mocking, should work with real MIME detection
        result = is_file_supported(fpath, ext)
        assert result is True, f"is_file_supported({ext}) returned False without mocking"

    # Simulate Magic failure by forcing fallback to extension-based detection
    # Use the same fallback set as defined in gui_scanner.py's exception handler
    fallback_exts = {
        '.txt', '.md', '.html', '.htm', '.json', '.xml', '.csv',
        '.yaml', '.yml', '.toml', '.ini', '.log', '.cfg', '.conf',
        '.py', '.pyw', '.js', '.jsx', '.ts', '.tsx', '.css', '.scss', '.less',
        '.sh', '.bash', '.zsh', '.fish', '.bat', '.cmd', '.ps1', '.psm1', '.psd1',
        '.rb', '.java', '.c', '.cpp', '.h', '.hpp', '.cc', '.cxx', '.hh', '.hxx',
        '.rs', '.go', '.php', '.swift', '.kt', '.kts', '.scala',
        '.cs', '.fs', '.vb', '.dart', '.lua', '.r', '.R', '.m', '.mm',
        '.hs', '.erl', '.hrl', '.ex', '.exs', '.elm', '.clj', '.cljs',
        '.sql', '.ddl', '.dml', '.pl', '.pm', '.tcl',
        '.markdown', '.rst', '.text', '.tsv',
        '.pdf',
        '.docx', '.pptx', '.xlsx',
        '.doc', '.ppt', '.xls',
        '.wps', '.et', '.dps',
        '.prototxt', '.pbtxt', '.solver', '.trainval', '.test',
        '.cfg',
        '.csproj', '.fsproj', '.vbproj',
        '.sln', '.user', '.vsconfig',
        '.xaml', '.axaml',
    }

    import src.gui_scanner as scanner
    # Reset cache so our mock takes effect
    scanner._mime_checker_cache = None

    monkeypatch.setattr(
        'src.gui_scanner._get_mime_checker',
        lambda: (None, (), set(), fallback_exts)
    )

    # After mocking to force fallback, all should still pass via extension check
    for ext, content in test_files.items():
        fpath = os.path.join(str(tmp_path), f'test{ext}')
        result = is_file_supported(fpath, ext)
        assert result is True, f"is_file_supported({ext}) returned False in fallback mode"

    # Test with unknown extension - should return False
    unknown_path = os.path.join(str(tmp_path), 'test.unknown_ext_xyz')
    with open(unknown_path, 'w') as f:
        f.write('test')
    result = is_file_supported(unknown_path, '.unknown_ext_xyz')
    assert result is False, "is_file_supported should return False for unknown extension in fallback"


@pytest.mark.parametrize("ext", ['.cs', '.xaml', '.sln', '.csproj', '.swift', '.kt', '.rs'])
def test_code_extensions_parsed_as_text(tmp_path, ext):
    """Specifically verify code-file extensions that were historically problematic
    (magic returns application/octet-stream for .cs on Windows) are parsed as text."""
    fname = f"test{ext}"
    filepath = os.path.join(str(tmp_path), fname)

    content_map = {
        '.xaml': '<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"><Grid/></Window>',
        '.sln': '\nMicrosoft Visual Studio Solution File, Format Version 12.00\n',
        '.swift': 'import Foundation\nlet x = 42\n',
        '.kt': 'package test\nfun main() { println(42) }\n',
        '.rs': 'fn main() { println!("hello"); }\n',
        '.cs': 'using System; class Test { static void Main() { } }',
    }
    content = content_map.get(ext, f"// test content for {ext} file\nint x = 42;")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    result = parse_file(filepath)
    assert result is not None, f"parse_file returned None for code extension {ext}"
    text = result.get("text", "").strip()
    assert len(text) > 0, f"Empty text for code extension {ext}"
    assert result["extract_type"] == "text", f"Expected text extract_type for {ext}"