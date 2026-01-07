"""Unit tests for subtask validation logic."""
import pytest

from app.api.routes.subtasks import ALLOWED_FILE_EXTENSIONS, MAX_FILE_SIZE_BYTES


class TestFileValidationConstants:
    def test_allowed_extensions_contains_expected_types(self):
        assert "json" in ALLOWED_FILE_EXTENSIONS
        assert "csv" in ALLOWED_FILE_EXTENSIONS
        assert "md" in ALLOWED_FILE_EXTENSIONS
        assert "txt" in ALLOWED_FILE_EXTENSIONS

    def test_max_file_size_is_10mb(self):
        expected_10mb = 10 * 1024 * 1024
        assert MAX_FILE_SIZE_BYTES == expected_10mb

    def test_disallowed_extensions_not_in_set(self):
        assert "exe" not in ALLOWED_FILE_EXTENSIONS
        assert "py" not in ALLOWED_FILE_EXTENSIONS
        assert "js" not in ALLOWED_FILE_EXTENSIONS
        assert "sh" not in ALLOWED_FILE_EXTENSIONS
