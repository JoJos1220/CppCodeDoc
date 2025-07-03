# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

"""
Application specific translation functionality.
Currently, only english/german is supported!
"""

import os
import json

from configSetup.configSetup import resource_path
from streamLogger.log_setup import logger

class Translator:
    """
    Translation class. It fungates as handshake to the translator files and enables
    the possibility to change language in realtime by key-values-pair parsing and changing
    language strings in form elements on screen.
    """
    def __init__(self, lang='en'):
        self.lang = lang
        self.translations = self.load_translations()

    def get_current_language(self):
        """
        Gathering current selected language by returning index value.
        """
        if self.lang == "en":
            return 0
        if self.lang == "de":
            return 1

        logger.log(f"Unsupported language: {self.lang}. Defaulting to English.", "warning")
        return 0

    def load_translations(self):
        """
        Loading Translations out of the json file, depending on selected language.
        """

        print(f"Try to open and load language file: lang/{self.lang}.json")

        # Path to translation file - depending on selected language
        file_path = resource_path(f"../lang/{self.lang}.json", f"assets/lang/{self.lang}.json")

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except FileNotFoundError:
                logger.log(f"Translation file not found: {file_path}", "error")
            except json.JSONDecodeError as e:
                logger.log(f"JSON decode error in {file_path}: {e}", "error")
            except OSError as e:
                logger.log(f"OS error while reading {file_path}: {e}", "error")
        else:
            logger.log(f"Translation file not found: {file_path}", "error")

        return {}

    def translate(self, key):
        """
        Translating element by key.
        Returning value, and if no key is found, the key will be returned as fallback
        """
        # supporting nested keys, e.g. "mainTabs.start"
        parts = key.split('.')
        value = self.translations
        for part in parts:
            value = value.get(part)
            if value is None:
                return key  # Fallback: returning key back
        return value
