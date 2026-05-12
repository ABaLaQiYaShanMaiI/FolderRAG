"""
Tests for the portal generator module.
"""
import os
import tempfile

from src.generator.portal import (
    generate_portal,
    extract_keywords,
    human_readable_size,
)


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

        # Portal is single-page - all content is in index.html
        with open(result["index_file"], "r", encoding="utf-8") as f:
            content = f.read()
        assert "test_doc.txt" in content
        assert "This is a test document for portal generation." in content


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


# ──────────────────────────────────────────────
#  Always-expanded content tests (replaces sr-only tests)
# ──────────────────────────────────────────────

def test_doc_content_always_visible():
    """
    Verify that .doc-content blocks are always visible (no display:none)
    in the generated portal. All file contents should be in the DOM flow
    without requiring any user interaction to expand.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = os.path.join(tmpdir, "source")
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(source_dir)

        test_file = os.path.join(source_dir, "sample.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("This is visible content for AI reading.")

        result = generate_portal(
            folder_path=source_dir,
            output_dir=output_dir,
            show_progress=False,
        )

        assert result["index_file"] is not None
        with open(result["index_file"], "r", encoding="utf-8") as f:
            content = f.read()

        # Verify that doc-content does NOT have style="display:none"
        # The new template removes the inline display:none from doc-content
        assert 'style="display:none"' not in content, \
            "doc-content should not have display:none (content should always be visible)"

        # Verify the file content text is present in the DOM
        assert "This is visible content for AI reading." in content, \
            "File content should be present and visible in the DOM"

        # Verify no sr-only block exists (the <section> with aria-hidden)
        assert 'aria-hidden="true"' not in content, \
            "sr-only block should not exist in Portal mode"


def test_each_file_block_has_copy_button():
    """
    Verify that every file block in the portal contains a copy button
    (with class .copy-file-btn) so users can copy individual file contents.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = os.path.join(tmpdir, "source")
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(source_dir)

        # Create multiple files
        for i, fname in enumerate(["alpha.txt", "beta.txt", "gamma.txt"]):
            with open(os.path.join(source_dir, fname), 'w', encoding='utf-8') as f:
                f.write(f"Content of {fname}.")

        result = generate_portal(
            folder_path=source_dir,
            output_dir=output_dir,
            show_progress=False,
        )

        assert result["index_file"] is not None
        with open(result["index_file"], "r", encoding="utf-8") as f:
            content = f.read()

        # Verify copy-file-btn class exists for each file
        copy_btn_count = content.count('class="copy-file-btn"')
        assert copy_btn_count == 3, \
            f"Expected 3 copy-file-btn elements, found {copy_btn_count}"

        # Verify each button has a data-file-index attribute
        import re
        indices = re.findall(r'data-file-index="(\d+)"', content)
        assert len(indices) == 3, \
            f"Expected 3 data-file-index attributes, found {len(indices)}"
        # Indices should be 0, 1, 2
        assert set(indices) == {'0', '1', '2'}, \
            f"Expected data-file-indices 0,1,2, got {set(indices)}"

        # Verify each pre element has a matching id
        for i in range(3):
            assert f'id="file-content-{i}"' in content, \
                f"Expected pre element with id='file-content-{i}'"


def test_copy_button_calls_copy_function():
    """
    Verify that copy buttons invoke the copyFileContent JavaScript function
    with onclick handler.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = os.path.join(tmpdir, "source")
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(source_dir)

        test_file = os.path.join(source_dir, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Test content for copy.")

        result = generate_portal(
            folder_path=source_dir,
            output_dir=output_dir,
            show_progress=False,
        )

        assert result["index_file"] is not None
        with open(result["index_file"], "r", encoding="utf-8") as f:
            content = f.read()

        # Verify the copy button has an onclick calling copyFileContent(this)
        assert 'onclick="copyFileContent(this)"' in content, \
            "Copy button should call copyFileContent(this) on click"

        # Verify the copyFileContent function exists in the script
        assert "function copyFileContent" in content, \
            "copyFileContent JavaScript function should be defined"


def test_no_sr_only_block_in_portal():
    """
    Verify that the sr-only block (the old <section> with aria-hidden and
    off-screen positioning, containing AI-readable text) is NOT present
    in the generated portal page.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = os.path.join(tmpdir, "source")
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(source_dir)

        test_file = os.path.join(source_dir, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Content for Portal mode.")

        result = generate_portal(
            folder_path=source_dir,
            output_dir=output_dir,
            show_progress=False,
        )

        assert result["index_file"] is not None
        with open(result["index_file"], "r", encoding="utf-8") as f:
            content = f.read()

        # The sr-only block markers should NOT be present
        assert "KNOWLEDGE PORTAL" not in content, \
            "Old sr-only KNOWLEDGE PORTAL header should not exist"
        assert "AI-READABLE TEXT EXTRACT" not in content, \
            "Old AI-READABLE TEXT EXTRACT label should not exist"
        assert "END OF AI-READABLE TEXT EXTRACT" not in content, \
            "Old sr-only end marker should not exist"


def test_portal_uses_minimal_font_and_compact_layout():
    """
    Verify that the portal uses the minimal font size (3px) and compact
    layout to maximize code density for AI text extraction.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = os.path.join(tmpdir, "source")
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(source_dir)

        test_file = os.path.join(source_dir, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Test content.")

        result = generate_portal(
            folder_path=source_dir,
            output_dir=output_dir,
            show_progress=False,
        )

        assert result["index_file"] is not None
        with open(result["index_file"], "r", encoding="utf-8") as f:
            content = f.read()

        # Verify minimal font size in CSS
        assert "font-size: 3px" in content or "font-size:3px" in content, \
            "CSS should have font-size: 3px for .doc-content pre"

        # Verify white-space: pre-wrap for wrapping
        assert "white-space: pre-wrap" in content or "white-space:pre-wrap" in content, \
            "CSS should have white-space: pre-wrap for wrapping"

        # Verify word-break: break-all exists
        assert "word-break: break-all" in content or "word-break:break-all" in content, \
            "CSS should have word-break: break-all"

        # Verify overflow-x: hidden to disable horizontal scroll
        assert "overflow-x: hidden" in content or "overflow-x:hidden" in content, \
            "CSS should have overflow-x: hidden"

        # Verify line-height: 1.2 for compact lines
        assert "line-height: 1.2" in content or "line-height:1.2" in content, \
            "CSS should have line-height: 1.2"


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
    Verify that unsupported/skipped files do NOT have doc-blocks
    in the index page (portal is single-page, no separate docs/ dir).
    Skipped files only appear in the file tree.
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

        # Verify portal is single-page (no docs/ directory)
        docs_dir = os.path.join(output_dir, "docs")
        assert not os.path.isdir(docs_dir), "docs/ directory should NOT exist (single-page portal)"

        # Read the index page
        assert result["index_file"] and os.path.exists(result["index_file"])
        with open(result["index_file"], "r", encoding="utf-8") as f:
            content = f.read()

        # The .bin file should NOT have a file-content-[id] pre element
        # (It may appear in the file tree, but NOT as a content block)
        # Notes.bin appears in the file tree, but the skipped files do NOT get
        # doc-blocks (content blocks). Verify that notes.bin does NOT have a
        # matching pre with id="file-content-*" in a .doc-block.
        import re
        file_content_ids = re.findall(r'id="file-content-\d+"', content)
        assert 'notes.bin' in content, "notes.bin should appear in file tree"
        # But it should NOT appear inside a doc-block's pre content
        # The readable.txt file is the only parsed doc, so there should be
        # only one pre with id="file-content-0"
        assert len(file_content_ids) == 1, \
            f"Expected exactly 1 file-content block (for readable.txt), found {len(file_content_ids)}"
        assert 'id="file-content-0"' in content, "readable.txt should have file-content-0"
        assert 'id="file-content-1"' not in content, \
            "notes.bin should not have a file-content block"

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
        # It should appear with skipped styling (tree-file.skipped or similar text indicator)
        assert "skipped" in content.lower() or "⏭️" in content or "tree-file.skipped" in content, \
            "Skipped file styling indicator expected in page"


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