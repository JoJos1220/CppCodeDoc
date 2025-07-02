import os
import json

from configSetup.configSetup import resource_path
from streamLogger.log_setup import logger

class Translator:
        def __init__(self, lang='en'):
            self.lang = lang
            self.translations = self.load_translations()

        def get_current_language(self):
            if self.lang == "en":
                return 0
            elif self.lang == "de":
                return 1
            else:
                logger.log(f"Unsupported language: {self.lang}. Defaulting to English.", "warning")
                return 0

        def load_translations(self):
            print(f"Try to open and load language file: lang/{self.lang}.json")

            # Pfad zur Übersetzungsdatei je nach Sprache
            file_path = resource_path(f"../lang/{self.lang}.json", f"assets/lang/{self.lang}.json")

            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        return json.load(file)
                except Exception as e:
                    logger.log(f"Error loading translation file: {e}", "error")
                    return {}
            else:
                logger.log(f"Translation file not found: {file_path}", "error")
                return {}

        def translate(self, key):
            # Unterstützt verschachtelte Schlüssel, z. B. "mainTabs.start"
            parts = key.split('.')
            value = self.translations
            for part in parts:
                value = value.get(part)
                if value is None:
                    return key  # Fallback: gib Key zurück, wenn nicht gefunden
            return value
    