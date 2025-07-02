# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import os
import sys
import pytest
from unittest.mock import mock_open, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.configSetup.configSetup import load_config, resource_path

@pytest.fixture
def fake_config_dict():
    return {
        "document": {
            "title": "TestDoc",
            "version": "2.0",
            "author": "Alice",
            "date": "2024-12-31",
            "logoPath": "custom/logo.svg",
            "highlightTodo": False,
            "showDocProgress": False
        },
        "source_dir": "./examples",
        "output_format": "pdf",
        "readonly": False,
        "headerCommentStyle": "///",
        "recursive": True,
        "output_path": "./NoWhereIsAnywhere/OrSomewhere",
        "backup_path": "./SomwhereIsNoBackup/AndNotAnywhere",
    }

def test_load_config_reads_and_parses_yaml(fake_config_dict):
    # Patch: open(), yaml.safe_load(), resource_path()
    with patch("builtins.open", mock_open(read_data="data")), \
         patch("yaml.safe_load", return_value=fake_config_dict), \
         patch("src.configSetup.configSetup.resource_path", side_effect=lambda a, b=None: a):

        config, _ = load_config("dummy_path.yaml")

    assert config["document"]["title"] == "TestDoc"
    assert config["document"]["author"] == "Alice"
    assert config["readonly"] is False
    assert config["output_format"] == ["pdf"]
    assert "source_dir" in config
    assert config["document"]["date"] == "2024-12-31"
    assert config["output_path"] == "./NoWhereIsAnywhere/OrSomewhere"

def test_load_config_auto_date(fake_config_dict):
    fake_config_dict["document"]["date"] = "auto"

    with patch("builtins.open", mock_open(read_data="data")), \
         patch("yaml.safe_load", return_value=fake_config_dict), \
         patch("src.configSetup.configSetup.resource_path", side_effect=lambda a, b=None: a):

        config, _ = load_config("dummy_path.yaml")

    from datetime import datetime
    today = datetime.today().strftime("%Y-%m-%d")
    assert config["document"]["date"] == today

def test_load_config_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError("File not found")), \
         patch("src.configSetup.configSetup.resource_path", return_value="nonexistent.yaml"):
        config_test, _ = load_config("nonexistent.yaml")
    assert config_test is None

def test_load_config_uses_default_when_path_is_empty(fake_config_dict):
    with patch("builtins.open", mock_open(read_data="data")), \
         patch("yaml.safe_load", return_value=fake_config_dict), \
         patch("src.configSetup.configSetup.resource_path", side_effect=lambda a, b=None: a):

        config, errors = load_config("")

    assert config["document"]["title"] == "TestDoc"
    assert errors is None

def test_resource_path_dev_mode():
    dev_path = os.path.join("dev", "resource", "file.txt")
    expected_end = os.path.normpath(dev_path)
    result = resource_path(dev_path)
    assert result.endswith(expected_end), f"{result} endet nicht auf {expected_end}"

def test_resource_path_exe_mode(monkeypatch):
    monkeypatch.setattr(sys, "_MEIPASS", "/fake/meipass", raising=False)
    result = resource_path("unused_dev_path", prod_path="assets/file.txt")
    assert result == os.path.normpath("/fake/meipass/assets/file.txt")
    monkeypatch.delenv("_MEIPASS", raising=False)

def test_load_config_parse_error_on_invalid_document_section():
    broken_config = {
        "document": "this_should_be_a_dict"
    }

    with patch("builtins.open", mock_open(read_data="data")), \
         patch("yaml.safe_load", return_value=broken_config), \
         patch("src.configSetup.configSetup.resource_path", side_effect=lambda a, b=None: a):

        config_test, errors = load_config("dummy_path.yaml")

    assert config_test is None
    assert errors is not None
    assert any("parsing" in e for e in errors)

def test_load_config_yaml_load_raises_exception():
    with patch("builtins.open", mock_open(read_data="data")), \
         patch("yaml.safe_load", side_effect=Exception("YAML broken")), \
         patch("src.configSetup.configSetup.resource_path", side_effect=lambda a, b=None: a):

        config_test, errors = load_config("dummy_path.yaml")

    assert config_test is None
    assert errors is not None
    assert any("Error loading config file" in e for e in errors)

def test_load_config_output_format_string(fake_config_dict):
    fake_config_dict["output_format"] = "pdf"

    with patch("builtins.open", mock_open(read_data="data")), \
         patch("yaml.safe_load", return_value=fake_config_dict), \
         patch("src.configSetup.configSetup.resource_path", side_effect=lambda a, b=None: a):

        config_test, errors = load_config("dummy_path.yaml")

    assert config_test["output_format"] == ["pdf"]
    assert errors is None

def test_load_config_missing_document_section():
    config_data = {
        "source_dir": "./examples",
        "output_format": "pdf"
    }

    with patch("builtins.open", mock_open(read_data="data")), \
         patch("yaml.safe_load", return_value=config_data), \
         patch("src.configSetup.configSetup.resource_path", side_effect=lambda a, b=None: a):

        config_test, errors = load_config("dummy_path.yaml")

    assert config_test["document"]["title"] == "📄 Documentation"
    assert config_test["document"]["author"] == "Unknown"
    assert "[configSetup] Missing key 'document' in section 'root' in config file 'dummy_path.yaml'" in errors