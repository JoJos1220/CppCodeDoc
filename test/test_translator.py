# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gui.translator import Translator

# Helping function to create a tem. translation file - only for pytest
def create_temp_translation_file(lang_code, data):
    """Helping function: Writing a temp. LanguageFile."""
    tmp_dir = tempfile.mkdtemp()
    file_path = os.path.join(tmp_dir, f"{lang_code}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return tmp_dir, file_path


def test_translate_existing_key(monkeypatch):
    data = {"mainTabs": {"start": "Starten"}}
    _, fake_file = create_temp_translation_file("de", data)

    monkeypatch.setattr("src.gui.translator.resource_path", lambda *args: fake_file)

    tr = Translator(lang="de")
    assert tr.translate("mainTabs.start") == "Starten"


def test_translate_missing_key(monkeypatch):
    data = {"mainTabs": {"start": "Starten"}}
    _, fake_file = create_temp_translation_file("de", data)

    monkeypatch.setattr("src.gui.translator.resource_path", lambda *args: fake_file)

    tr = Translator(lang="de")
    assert tr.translate("unknown.key") == "unknown.key"


def test_translate_missing_file(monkeypatch):
    monkeypatch.setattr("src.gui.translator.resource_path", lambda *args: "/non/existent/path.json")

    tr = Translator(lang="de")
    assert tr.translate("any.key") == "any.key"  # No key found


def test_get_current_language():
    assert Translator("en").get_current_language() == 0
    assert Translator("de").get_current_language() == 1
    assert Translator("fr").get_current_language() == 0  # Fallback
