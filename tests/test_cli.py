"""
Tests for the CLI (generate.py) — TXT export mode and portal mode.
"""

import os
import sys
import subprocess
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, PROJECT_ROOT)

GENERATE_SCRIPT = os.path.join(PROJECT_ROOT, "generate.py")

# ──────────────────────────────────────────────
#  Fixtures
# ──────────────────────────────────────────────

def _create_sample_folder(tmpdir: str) -> str:
    """Create a folder with sample files for testing."""
    folder = os.path.join(tmpdir, "sample_docs")
    os.makedirs(folder, exist_ok=True)

    # Text file
    with open(os.path.join(folder, "hello.txt"), "w", encoding="utf-8") as f:
        f.write("Hello, this is a sample text file for FolderKnowledgeSiteGeneratorForAI testing.\nIt has multiple lines.\n")

    # Markdown file
    with open(os.path.join(folder, "readme.md"), "w", encoding="utf-8") as f:
        f.write("# Sample Document\n\nThis is a Markdown file with some **bold** text.\n")

    # CSV file (supported via fallback extension list)
    with open(os.path.join(folder, "notes.csv"), "w", encoding="utf-8") as f:
        f.write("id,name,value\n1,test,100\n2,demo,200\n")

    return folder


# ──────────────────────────────────────────────
#  Helper: run generate.py as subprocess
# ──────────────────────────────────────────────

def _run_generate(args: list) -> tuple:
    """Run generate.py with given args and return (returncode, stdout, stderr)."""
    cmd = [sys.executable, GENERATE_SCRIPT] + args
    # Use utf-8 encoding explicitly to handle Chinese output on Windows
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result.returncode, result.stdout, result.stderr


# ──────────────────────────────────────────────
#  Tests — TXT Export Mode (default, no --portal)
# ──────────────────────────────────────────────

class TestTextExportMode:
    """Test the traditional TXT export mode (default, no --portal)."""

    def test_basic_text_export(self, tmp_path):
        """Generate a TXT file from sample docs."""
        folder = _create_sample_folder(str(tmp_path))
        output = os.path.join(str(tmp_path), "output.txt")

        rc, stdout, stderr = _run_generate([folder, "-o", output])

        assert rc == 0, f"Expected exit code 0, got {rc}. stderr: {stderr}"
        assert os.path.exists(output), f"Output file not found: {output}"
        assert os.path.getsize(output) > 0, "Output file is empty"
        assert "OK" in stdout, f"Unexpected stdout: {stdout}"

        # Verify plain text structure (TXT mode)
        with open(output, "r", encoding="utf-8") as f:
            content = f.read()
        # TXT mode uses file: headers
        assert "hello.txt" in content

    def test_extension_appended(self, tmp_path):
        """Verify .txt extension is appended when missing."""
        folder = _create_sample_folder(str(tmp_path))
        output = os.path.join(str(tmp_path), "output")  # No extension

        rc, stdout, stderr = _run_generate([folder, "-o", output])
        assert rc == 0
        # TXT mode appends .txt
        expected = output + ".txt"
        assert os.path.exists(expected), f"Expected {expected} to exist"

    def test_max_chars_limit(self, tmp_path):
        """Verify --max-chars truncates file content."""
        folder = _create_sample_folder(str(tmp_path))
        output = os.path.join(str(tmp_path), "output_truncated.txt")

        # Use small max-chars value
        rc, stdout, stderr = _run_generate([folder, "-o", output, "--max-chars", "20"])

        assert rc == 0, f"Expected exit code 0, got {rc}. stderr: {stderr}"
        assert os.path.exists(output)

        with open(output, "r", encoding="utf-8") as f:
            content = f.read()
        # Should contain truncation indicator
        assert "[Truncated at" in content, f"Missing truncation marker in: {content[:500]}"
        # Unlimited output would be ~600+ chars; truncated should be < ~550
        assert len(content) < 550, f"Expected truncated file < 550 chars, got {len(content)}"

    def test_missing_folder(self, tmp_path):
        """Verify error on non-existent folder."""
        output = os.path.join(str(tmp_path), "output.txt")
        rc, stdout, stderr = _run_generate(["/nonexistent/path", "-o", output])
        assert rc != 0, "Expected non-zero exit for invalid folder"

    def test_no_output_flag(self, tmp_path):
        """Verify error when -o is missing."""
        folder = _create_sample_folder(str(tmp_path))
        rc, stdout, stderr = _run_generate([folder])
        assert rc != 0, "Expected non-zero exit when -o is missing"
        # Should print usage/error
        assert "usage" in stdout.lower() or "error" in stderr.lower()


# ──────────────────────────────────────────────
#  Tests — Portal Mode
# ──────────────────────────────────────────────

class TestPortalMode:
    """Test the portal (single-page) generation mode."""

    def test_basic_portal_generation(self, tmp_path):
        """Generate a portal from sample docs."""
        folder = _create_sample_folder(str(tmp_path))
        output_dir = os.path.join(str(tmp_path), "portal_output")

        rc, stdout, stderr = _run_generate([
            folder, "--portal", "-o", output_dir,
        ])

        assert rc == 0, f"Expected exit code 0, got {rc}. stderr: {stderr}"
        assert os.path.isdir(output_dir), f"Output dir not created: {output_dir}"
        assert os.path.exists(os.path.join(output_dir, "index.html")), "index.html not found"
        assert "知识门户" in stdout or "Portal" in stdout or "门户" in stdout

        # Verify index.html structure
        index_path = os.path.join(output_dir, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "FolderKnowledgeSiteGeneratorForAI" in content or "folder-knowledge" in content
        assert "sample_docs" in content

    def test_portal_page_creation(self, tmp_path):
        """Verify that portal is single-page: no docs/ dir, all content in index.html."""
        folder = _create_sample_folder(str(tmp_path))
        output_dir = os.path.join(str(tmp_path), "portal_pages")

        rc, stdout, stderr = _run_generate([
            folder, "--portal", "-o", output_dir,
        ])
        assert rc == 0

        # Portal is single-page — no docs/ subdirectory
        docs_dir = os.path.join(output_dir, "docs")
        assert not os.path.isdir(docs_dir), "docs/ subdirectory should NOT exist (single-page portal)"

        # All content is in index.html
        index_path = os.path.join(output_dir, "index.html")
        assert os.path.isfile(index_path), "index.html should exist"
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Verify file contents are embedded directly in index.html
        assert "hello.txt" in content, "hello.txt content should be in index.html"
        assert "readme.md" in content, "readme.md content should be in index.html"

    def test_portal_skipped_flag(self, tmp_path):
        """Verify --no-skipped works (all supported files so no effect)."""
        folder = _create_sample_folder(str(tmp_path))
        output_dir = os.path.join(str(tmp_path), "portal_no_skipped")

        rc, stdout, stderr = _run_generate([
            folder, "--portal", "-o", output_dir,
            "--no-skipped"
        ])
        assert rc == 0

    def test_portal_missing_folder(self, tmp_path):
        """Verify error on non-existent folder in portal mode."""
        output_dir = os.path.join(str(tmp_path), "portal_empty")
        rc, stdout, stderr = _run_generate([
            "/nonexistent/path", "--portal", "-o", output_dir
        ])
        assert rc != 0, "Expected non-zero exit for invalid folder in portal mode"


# ──────────────────────────────────────────────
#  Tests — CLI Argument Validation
# ──────────────────────────────────────────────

class TestCLIArgs:
    """Test CLI argument parsing and validation."""

    def test_help_output(self):
        """Verify --help prints usage information."""
        rc, stdout, stderr = _run_generate(["--help"])
        assert rc == 0
        assert "FolderKnowledgeSiteGeneratorForAI" in stdout or "folderknowledge" in stdout.lower()
        assert "--portal" in stdout

    def test_version_or_name(self):
        """Verify basic CLI identification."""
        rc, stdout, stderr = _run_generate(["--help"])
        assert rc == 0
        # Should mention both modes
        assert "传统模式" in stdout or "single" in stdout.lower() or "HTML" in stdout
        assert "门户模式" in stdout or "portal" in stdout.lower()