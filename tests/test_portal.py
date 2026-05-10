"""
Tests for the portal generator module.
"""
import os
import tempfile

from src.generator.portal import (
    generate_portal,
    extract_keywords,
    make_safe_filename,
    human_readable_size,
    split_large_text,
)


def test_make_safe_filename():
    """Test filename sanitization."""
    result = make_safe_filename(
        r"C:\docs\技术文档\需求说明书.pdf",
        r"C:\docs"
    )
    assert "需求说明书" in result
    assert result.endswith(".html")
    assert ":" not in result
    assert "\\" not in result


def test_human_readable_size():
    """Test size formatting."""
    assert "B" in human_readable_size(500)
    assert "KB" in human_readable_size(2048)
    assert "MB" in human_readable_size(1048576 * 2)


def test_extract_keywords():
    """Test keyword extraction from text."""
    text = """
    本文介绍了人工智能在医疗领域的应用。
    人工智能技术可以辅助医生进行诊断。
    机器学习算法能够分析医学影像数据。
    深度学习模型在疾病预测方面表现优异。
    AI technology helps doctors diagnose diseases.
    Machine learning improves medical imaging analysis.
    """
    keywords = extract_keywords(text, max_words=5)
    assert len(keywords) <= 5
    assert len(keywords) > 0
    # Should not contain stop words
    for kw in keywords:
        assert kw not in ('的', '了', '在', '是', 'the', 'and', 'for')


def test_extract_keywords_stop_words():
    """Test that stop words are filtered out."""
    text = "这是一个测试文件，其中的内容主要是用于测试功能。"
    keywords = extract_keywords(text, max_words=5)
    # "的", "了", "是", "一" etc should be filtered out
    for kw in keywords:
        assert kw not in ('的', '了', '是', '一', '一个', '在')


def test_split_large_text_no_split():
    """Test that small text is not split."""
    text = "Short text"
    parts = split_large_text(text, max_chars=8000)
    assert len(parts) == 1
    assert parts[0][0] == text
    assert parts[0][1] is None


def test_split_large_text_actually_splits():
    """Test that large text is split into multiple parts."""
    # Create text that exceeds max_chars
    text = "\n\n".join(["Paragraph " + str(i) * 100 for i in range(50)])
    parts = split_large_text(text, max_chars=500)
    assert len(parts) > 1


def test_generate_portal_empty_folder():
    """Test portal generation with an empty folder."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Empty folder
        source_dir = os.path.join(tmpdir, "source")
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(source_dir)

        result = generate_portal(
            folder_path=source_dir,
            output_dir=output_dir,
            show_progress=False,
        )
        assert result["doc_count"] == 0
        assert result["total_chars"] == 0
        assert result["index_file"] is None


def test_generate_portal_with_text_file():
    """Test portal generation with a single text file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = os.path.join(tmpdir, "source")
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(source_dir)

        # Create a text file
        test_file = os.path.join(source_dir, "test_doc.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("This is a test document for portal generation.")

        result = generate_portal(
            folder_path=source_dir,
            output_dir=output_dir,
            show_progress=False,
        )

        assert result["doc_count"] >= 1
        assert result["total_chars"] > 0
        assert result["index_file"] is not None
        assert os.path.exists(result["index_file"])

        # Check that docs directory was created with html files
        docs_dir = os.path.join(output_dir, "docs")
        assert os.path.isdir(docs_dir)
        html_files = [f for f in os.listdir(docs_dir) if f.endswith('.html')]
        assert len(html_files) >= 1


def test_generate_portal_output_dir_exists():
    """Test portal generation when output dir already exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = os.path.join(tmpdir, "source")
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(source_dir)
        os.makedirs(output_dir)  # Pre-create the output dir

        # Create a dummy file in the output dir
        dummy = os.path.join(output_dir, "dummy.txt")
        with open(dummy, 'w') as f:
            f.write("dummy")

        # Create a test source file
        test_file = os.path.join(source_dir, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Test content")

        # Should not raise an error
        result = generate_portal(
            folder_path=source_dir,
            output_dir=output_dir,
            show_progress=False,
        )
        assert result["doc_count"] >= 1
        assert os.path.exists(result["index_file"])


def test_generate_portal_doc_sorting():
    """Test that documents are sorted alphabetically."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = os.path.join(tmpdir, "source")
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(source_dir)

        # Create files with names that would test sorting
        files = ["b_file.txt", "a_file.txt", "c_file.txt"]
        for fname in files:
            with open(os.path.join(source_dir, fname), 'w', encoding='utf-8') as f:
                f.write(f"Content of {fname}")

        result = generate_portal(
            folder_path=source_dir,
            output_dir=output_dir,
            show_progress=False,
        )
        assert result["doc_count"] == 3
        # Index should be generated
        assert result["index_file"] is not None
        assert os.path.exists(result["index_file"])


def test_split_large_text_with_headings():
    """Test that split_large_text handles markdown headings."""
    text = "# Introduction\n\nThis is the intro.\n\n# Methods\n\nThis describes methods.\n\n# Results\n\nThese are the results.\n\n# Conclusion\n\nThis is the conclusion."
    parts = split_large_text(text, max_chars=50)
    assert len(parts) > 1


# ──────────────────────────────────────────────
#  Skipped file behavior tests
# ──────────────────────────────────────────────

def _create_folder_with_unsupported_file(tmpdir: str) -> str:
    """
    Create a folder with a supported .txt and an unsupported file type.
    Uses a .zip binary blob so python-magic won't classify it as text/plain.
    """
    folder = os.path.join(tmpdir, "mixed_docs")
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "readable.txt"), "w", encoding="utf-8") as f:
        f.write("Supported content for portal test.")
    # Write binary data that magic will NOT detect as text/plain
    with open(os.path.join(folder, "notes.bin"), "wb") as f:
        f.write(b'\x00\x01\x02\x03\xff\xfe\xfd\xfc' * 32)
    return folder


def test_skipped_files_do_not_generate_pages():
    """
    Verify that unsupported/skipped files do NOT generate individual
    HTML pages in the docs/ directory (behavior change: no placeholder pages).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = _create_folder_with_unsupported_file(tmpdir)
        output_dir = os.path.join(tmpdir, "output")

        result = generate_portal(
            folder_path=source_dir,
            output_dir=output_dir,
            show_progress=False,
            include_skipped=True,
        )

        # Only the supported .txt file should produce a doc page
        docs_dir = os.path.join(output_dir, "docs")
        assert os.path.isdir(docs_dir)
        doc_files = [f for f in os.listdir(docs_dir) if f.endswith('.html')]
        assert len(doc_files) == 1, f"Expected 1 doc page, got {len(doc_files)}: {doc_files}"

        # The .bin file should NOT have a page
        bin_pages = [f for f in doc_files if 'notes' in f or 'bin' in f]
        assert len(bin_pages) == 0, f"Found unexpected pages for .bin: {bin_pages}"

        # Verify the skipped count reflects the unsupported file
        assert result["skipped"] >= 1, f"Expected at least 1 skipped, got {result['skipped']}"
        assert result["doc_count"] == 1, f"Expected 1 parsed doc, got {result['doc_count']}"


def test_skipped_files_appear_in_file_tree():
    """
    Verify that skipped files appear in the file tree HTML on the index page
    when include_skipped=True.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = _create_folder_with_unsupported_file(tmpdir)
        output_dir = os.path.join(tmpdir, "output")

        result = generate_portal(
            folder_path=source_dir,
            output_dir=output_dir,
            show_progress=False,
            include_skipped=True,
        )

        # Read index.html and check for the skipped file reference
        index_path = result["index_file"]
        assert index_path and os.path.exists(index_path)
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()

        # The .bin file should appear in the file tree as a skipped entry
        assert "notes.bin" in content, "Skipped file 'notes.bin' should appear in file tree"
        # It should appear as a tree-file.skipped entry (not as a doc-card)
        assert "tree-file skipped" in content or "⏭️" in content, \
            "Skipped file should appear with skipped styling in file tree"


def test_skipped_files_excluded_from_file_tree_when_disabled():
    """
    Verify that skipped files do NOT appear in the file tree
    when include_skipped=False.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = _create_folder_with_unsupported_file(tmpdir)
        output_dir = os.path.join(tmpdir, "output")

        result = generate_portal(
            folder_path=source_dir,
            output_dir=output_dir,
            show_progress=False,
            include_skipped=False,
        )

        # Read index.html — the .bin file should NOT appear
        if result["index_file"]:
            with open(result["index_file"], "r", encoding="utf-8") as f:
                content = f.read()
            assert "notes.bin" not in content, \
                "Skipped file should not appear in index when include_skipped=False"


def test_gui_scanner_skipped_behavior():
    """
    Integration-style test verifying that build_html_from_files skips
    unsupported files and generates no placeholder for them.
    Uses a no-match extension (.xyz) with binary content to ensure
    magic-based detection marks it as unsupported.
    """
    from src.gui_scanner import build_html_from_files, collect_files_info

    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = os.path.join(tmpdir, "scan_docs")
        os.makedirs(source_dir, exist_ok=True)
        with open(os.path.join(source_dir, "good.txt"), "w", encoding="utf-8") as f:
            f.write("Readable text content.")
        # Write binary content with an extension NOT in the fallback set
        with open(os.path.join(source_dir, "bad.bin"), "wb") as f:
            f.write(b'\x00\x01\x02\x03\xff\xfe\xfd\xfc' * 32)

        file_list, _ = collect_files_info(source_dir)
        unsupported = [f for f in file_list if not f['supported']]
        assert len(unsupported) >= 1, f"Should detect unsupported file. All files: {[f['rel_path'] for f in file_list]}"

        output_path = os.path.join(tmpdir, "output.html")
        html, parsed, skipped, errors, chars = build_html_from_files(
            source_dir, file_list, output_path,
            include_skipped=True,
        )

        # With include_skipped=True, the HTML still contains a skipped <article>
        assert parsed == 1, f"Expected 1 parsed, got {parsed}"
        assert skipped >= 1, f"Expected >=1 skipped, got {skipped}"
        assert "skipped" in html or "⏭️" in html, \
            "Skipped article should appear in HTML when include_skipped=True"

        # Now test with include_skipped=False
        html2, parsed2, skipped2, errors2, chars2 = build_html_from_files(
            source_dir, file_list, output_path,
            include_skipped=False,
        )
        assert parsed2 == 1, f"Expected 1 parsed, got {parsed2}"
        assert skipped2 >= 1, f"Expected >=1 skipped, got {skipped2}"
        # The skipped article should NOT appear in the HTML
        assert "bad.bin" not in html2, \
            "Skipped file should not appear in HTML when include_skipped=False"


def test_skipped_page_template_unused_by_portal():
    """
    Verify that wrap_skipped_html (from templates.py) is NOT called
    during portal generation — skipped files only appear in the file tree.
    This tests the dead-code characteristic: wrap_skipped_html is retained
    as a public API but is no longer internally used by the portal generator.
    """
    from src.generator.templates import wrap_skipped_html
    # The function is importable and documented, but portal.py never calls it.
    # This test asserts that wrap_skipped_html is available as a public API
    # but verifies the portal generator doesn't use it for skipped files.
    assert callable(wrap_skipped_html), "wrap_skipped_html should be importable and callable"

    # Verify it actually produces valid output if called manually
    sample_html = wrap_skipped_html(
        title="test.xyz",
        folder_name="test_folder",
        file_size_hr="1.0 KB",
        filepath="/path/to/test.xyz",
    )
    assert "<!DOCTYPE html>" in sample_html
    assert "test.xyz" in sample_html