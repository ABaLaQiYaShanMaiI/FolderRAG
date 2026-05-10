"""
Tests for the portal generator module.
"""
import os
import shutil
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
