import pytest
from pathlib import Path


def test_read_file_success(tmp_path):
    from evokb.core.utils import read_file

    test_file = tmp_path / "test.md"
    test_file.write_text("# Hello World")

    content = read_file(test_file)
    assert content == "# Hello World"


def test_read_file_nonexistent():
    from evokb.core.utils import read_file

    result = read_file(Path("/nonexistent/file.md"))
    assert result == ""


def test_read_file_with_encoding(tmp_path):
    from evokb.core.utils import read_file

    test_file = tmp_path / "test.md"
    test_file.write_text("Test content with special chars: éàü")

    content = read_file(test_file)
    assert "Test content" in content


def test_list_files_empty(tmp_path):
    from evokb.core.utils import list_files

    files = list_files(tmp_path)
    assert files == []


def test_list_files_with_pattern(tmp_path):
    from evokb.core.utils import list_files

    (tmp_path / "file1.md").write_text("content")
    (tmp_path / "file2.md").write_text("content")
    (tmp_path / "file3.txt").write_text("content")

    md_files = list_files(tmp_path, "*.md")
    assert len(md_files) == 2


def test_list_files_recursive(tmp_path):
    from evokb.core.utils import list_files

    (tmp_path / "file1.md").write_text("content")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "file2.md").write_text("content")

    files = list_files(tmp_path, "**/*.md")
    assert len(files) == 2


def test_ensure_dir_creates(tmp_path):
    from evokb.core.utils import ensure_dir

    new_dir = tmp_path / "new_folder" / "nested"
    result = ensure_dir(new_dir)

    assert new_dir.exists()
    assert result == new_dir


def test_ensure_dir_returns_existing(tmp_path):
    from evokb.core.utils import ensure_dir

    existing_dir = tmp_path / "existing"
    existing_dir.mkdir()

    result = ensure_dir(existing_dir)

    assert existing_dir.exists()
    assert result == existing_dir
