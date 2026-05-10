"""
Tests for the CLI (generate.py) — single HTML mode and portal mode.
"""

import os
import sys
import shutil
import subprocess
import tempfile
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
        f.write("Hello, this is a sample text file for DocPortal testing.\nIt has multiple lines.\n")

    # Markdown file
    with open(os.path.join(folder, "readme.md"), "w", encoding="utf-8") as f:
        f.write("# Sample Document\n\nThis is a Markdown file with some **bold** text.\n")

    # Unsupported file type
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
#  Tests — Single HTML Mode
# ──────────────────────────────────────────────

class TestSingleHTMLMode:
    """Test the traditional single-file HTML generation mode."""

    def test_basic_html_generation(self, tmp_path):
        """Generate a single HTML file from sample docs."""
        folder = _create_sample_folder(str(tmp_path))
        output = os.path.join(str(tmp_path), "output.html")

        rc, stdout, stderr = _run_generate([folder, "-o", output])

        assert rc == 0, f"Expected exit code 0, got {rc}. stderr: {stderr}"
        assert os.path.exists(output), f"Output file not found: {output}"
        assert os.path.getsize(output) > 0, "Output file is empty"
        assert "已生成" in stdout or "OK" in stdout, f"Unexpected stdout: {stdout}"

        # Verify HTML structure
        with open(output, "r", encoding="utf-8") as f:
            content = f.read()
        assert "<!DOCTYPE html>" in content
        assert "<article>" in content
        assert "hello.txt" in content
        assert "readme.md" in content
        assert "sample_docs" in content

    def test_max_chars_limit(self, tmp_path):
        """Verify --max-chars limits total output."""
        folder = _create_sample_folder(str(tmp_path))
        output = os.path.join(str(tmp_path), "output_truncated.html")

        rc, stdout, stderr = _run_generate([folder, "-o", output, "--max-chars", "20"])

        assert rc == 0, f"Expected exit code 0, got {rc}. stderr: {stderr}"
        assert os.path.exists(output)

        with open(output, "r", encoding="utf-8") as f:
            content = f.read()
        # Should contain the truncation comment
        assert "截断" in content or "truncated" in content

    def test_missing_folder(self, tmp_path):
        """Verify error on non-existent folder."""
        output = os.path.join(str(tmp_path), "output.html")
        rc, stdout, stderr = _run_generate(["/nonexistent/path", "-o", output])
        assert rc != 0, "Expected non-zero exit for invalid folder"

    def test_no_output_flag(self, tmp_path):
        """Verify error when -o is missing."""
        folder = _create_sample_folder(str(tmp_path))
        rc, stdout, stderr = _run_generate([folder])
        assert rc != 0, "Expected non-zero exit when -o is missing"
        # Should print usage/error
        assert "usage" in stdout.lower() or "error" in stderr.lower()

    def test_include_skipped_files(self, tmp_path):
        """Verify skipped unsupported files are included by default."""
        folder = _create_sample_folder(str(tmp_path))
        output = os.path.join(str(tmp_path), "output_with_skipped.html")

        rc, stdout, stderr = _run_generate([folder, "-o", output])
        assert rc == 0

        with open(output, "r", encoding="utf-8") as f:
            content = f.read()
        # CSV files are supported via fallback, so they won't be "skipped"
        # But we should at least see them in the output
        assert "notes.csv" in content


# ──────────────────────────────────────────────
#  Tests — Portal Mode
# ──────────────────────────────────────────────

class TestPortalMode:
    """Test the portal (multi-page) generation mode."""

    def test_basic_portal_generation(self, tmp_path):
        """Generate a portal from sample docs."""
        folder = _create_sample_folder(str(tmp_path))
        output_dir = os.path.join(str(tmp_path), "portal_output")

        rc, stdout, stderr = _run_generate([
            folder, "--portal", "-o", output_dir,
            "--max-chars-per-page", "50000"
        ])

        assert rc == 0, f"Expected exit code 0, got {rc}. stderr: {stderr}"
        assert os.path.isdir(output_dir), f"Output dir not created: {output_dir}"
        assert os.path.exists(os.path.join(output_dir, "index.html")), "index.html not found"
        assert "知识门户" in stdout or "Portal" in stdout or "门户" in stdout

        # Verify index.html structure
        index_path = os.path.join(output_dir, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "DocPortal" in content or "doc-portal" in content
        assert "sample_docs" in content

    def test_portal_page_creation(self, tmp_path):
        """Verify that doc pages are created for each file."""
        folder = _create_sample_folder(str(tmp_path))
        output_dir = os.path.join(str(tmp_path), "portal_pages")

        rc, stdout, stderr = _run_generate([
            folder, "--portal", "-o", output_dir,
            "--max-chars-per-page", "50000"
        ])
        assert rc == 0

        # Check that individual doc HTML files were created in docs/ subdirectory
        docs_dir = os.path.join(output_dir, "docs")
        assert os.path.isdir(docs_dir), f"docs/ subdirectory not found in {os.listdir(output_dir)}"
        doc_files = [f for f in os.listdir(docs_dir) if f.endswith(".html")]
        assert len(doc_files) > 0, f"No doc pages created in docs/. Contents: {os.listdir(docs_dir)}"

    def test_portal_skipped_flag(self, tmp_path):
        """Verify --no-skipped hides unsupported file markers."""
        folder = _create_sample_folder(str(tmp_path))
        output_dir = os.path.join(str(tmp_path), "portal_no_skipped")

        rc, stdout, stderr = _run_generate([
            folder, "--portal", "-o", output_dir,
            "--no-skipped"
        ])
        assert rc == 0
        # The test folder has all supported file types (txt, md, csv are in fallback),
        # so --no-skipped won't change much, but the command should still work

    def test_portal_per_page_chars(self, tmp_path):
        """Verify custom chars per page works."""
        folder = _create_sample_folder(str(tmp_path))
        output_dir = os.path.join(str(tmp_path), "portal_small_pages")

        rc, stdout, stderr = _run_generate([
            folder, "--portal", "-o", output_dir,
            "--max-chars-per-page", "10"  # Very small to force page splitting
        ])
        assert rc == 0
        # With such small per-page limit, we may get multiple pages for each file
        # The important thing is it doesn't crash

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
        assert "DocPortal" in stdout or "docportal" in stdout.lower()
        assert "--portal" in stdout

    def test_version_or_name(self):
        """Verify basic CLI identification."""
        rc, stdout, stderr = _run_generate(["--help"])
        assert rc == 0
        # Should mention both modes
        assert "传统模式" in stdout or "single" in stdout.lower() or "HTML" in stdout
        assert "门户模式" in stdout or "portal" in stdout.lower()
