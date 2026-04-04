import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_apply_change_creates_backup(tmp_path):
    from evokb.eval.evaluator import apply_change

    test_file = tmp_path / "test.md"
    test_file.write_text("original content")

    result = apply_change(test_file, "new content")
    backup_file = tmp_path / "test.md.bak"

    assert result is True
    assert test_file.read_text() == "new content"
    assert backup_file.exists()
    assert backup_file.read_text() == "original content"


def test_apply_change_no_backup_for_new_file(tmp_path):
    from evokb.eval.evaluator import apply_change

    test_file = tmp_path / "new.md"

    result = apply_change(test_file, "new content", backup=True)

    assert result is True
    assert test_file.read_text() == "new content"


def test_apply_change_disabled_backup(tmp_path):
    from evokb.eval.evaluator import apply_change

    test_file = tmp_path / "test.md"
    test_file.write_text("original")

    result = apply_change(test_file, "new", backup=False)
    backup_file = tmp_path / "test.md.bak"

    assert result is True
    assert not backup_file.exists()


def test_revert_change(tmp_path):
    from evokb.eval.evaluator import apply_change, revert_change

    test_file = tmp_path / "test.md"
    test_file.write_text("original")
    backup_file = tmp_path / "test.md.bak"
    backup_file.write_text("backup content")

    result = revert_change(test_file)

    assert result is True
    assert test_file.read_text() == "backup content"
    assert not backup_file.exists()


def test_revert_change_no_backup(tmp_path):
    from evokb.eval.evaluator import revert_change

    test_file = tmp_path / "test.md"
    test_file.write_text("current")

    result = revert_change(test_file)

    assert result is False


@patch("evokb.eval.evaluator.completion")
def test_score_change_parses_json(mock_completion):
    from evokb.eval.evaluator import score_change

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content='{"clarity": 8, "grounding": 9, "coverage": 7, "backlinks": 6, "overall": 8}'
            )
        )
    ]
    mock_completion.return_value = mock_response

    result = score_change("test content", ["clarity", "grounding"])

    assert "scores" in result
    assert result["overall"] == 8
    assert result["passed"] is True


@patch("evokb.eval.evaluator.completion")
def test_score_change_fails_below_threshold(mock_completion):
    from evokb.eval.evaluator import score_change

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"clarity": 5, "overall": 5}'))
    ]
    mock_completion.return_value = mock_response

    result = score_change("test content", ["clarity"])

    assert result["overall"] == 5
    assert result["passed"] is False


@patch("evokb.eval.evaluator.completion")
def test_score_change_handles_error(mock_completion):
    from evokb.eval.evaluator import score_change

    mock_completion.side_effect = Exception("API Error")

    result = score_change("test content", ["clarity"])

    assert "error" in result
    assert result["overall"] == 0
    assert result["passed"] is False
