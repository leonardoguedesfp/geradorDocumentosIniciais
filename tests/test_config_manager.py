"""Tests for config_manager module."""

import json
import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

from app.core.config_manager import load_config, save_config, get_templates_folder, set_templates_folder


@pytest.fixture
def tmp_config(tmp_path):
    """Patch _get_config_path to use a temp directory."""
    config_path = tmp_path / "config.json"
    with patch("app.core.config_manager._get_config_path", return_value=config_path):
        yield config_path


class TestLoadConfig:
    def test_load_missing_file(self, tmp_config):
        result = load_config()
        assert result == {}

    def test_load_valid_config(self, tmp_config):
        tmp_config.write_text('{"templates_folder": "/some/path"}', encoding="utf-8")
        result = load_config()
        assert result == {"templates_folder": "/some/path"}

    def test_load_corrupt_json(self, tmp_config):
        tmp_config.write_text("not json", encoding="utf-8")
        result = load_config()
        assert result == {}

    def test_load_empty_file(self, tmp_config):
        tmp_config.write_text("", encoding="utf-8")
        result = load_config()
        assert result == {}


class TestSaveConfig:
    def test_save_creates_file(self, tmp_config):
        save_config({"templates_folder": "/test/path"})
        assert tmp_config.exists()
        data = json.loads(tmp_config.read_text(encoding="utf-8"))
        assert data["templates_folder"] == "/test/path"

    def test_save_overwrites(self, tmp_config):
        save_config({"templates_folder": "/first"})
        save_config({"templates_folder": "/second"})
        data = json.loads(tmp_config.read_text(encoding="utf-8"))
        assert data["templates_folder"] == "/second"


class TestGetSetTemplatesFolder:
    def test_get_empty_when_no_config(self, tmp_config):
        assert get_templates_folder() == ""

    def test_set_and_get(self, tmp_config):
        set_templates_folder("/my/templates")
        assert get_templates_folder() == "/my/templates"

    def test_get_missing_key(self, tmp_config):
        save_config({"other_key": "value"})
        assert get_templates_folder() == ""
