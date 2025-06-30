# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys, os

from datetime import datetime
from configSetup.installModules import ensure_modules

ensure_modules([("yaml", "pyYAML")])
import yaml

def load_config(config_path = ""):
    errors = []
    
    def get_with_fallback(d, key, fallback, section="root"):
        value = d.get(key, fallback)
        if key not in d:
            errors.append(f"[configSetup] Missing key '{key}' in section '{section}', using fallback: {repr(fallback)}")
        return value

    def try_load_and_parse(path):
        config, used_path, load_error = _try_load(path)
        if load_error:
            errors.append(load_error)
            return None

        result, parse_error = _try_parse(config, used_path)
        if parse_error:
            errors.append(parse_error)
            return None
        return result

    def _try_load(path):
        if path == "":
            path = resource_path( "../config.yaml", "assets/config.yaml")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f), path, None
        except Exception as e:
            return None, path, f"[configSetup] Error loading config file '{path}': {e}"

    def _try_parse(config_data, used_path):
        try:
            doc = config_data.get("document", {})
            if "document" not in config_data:
                errors.append(f"[configSetup] Missing key 'document' in section 'root' in config file '{used_path}'")

            raw_date = get_with_fallback(doc, "date", "auto", "document")
            date = datetime.today().strftime("%Y-%m-%d") if str(raw_date).strip().lower() in ("auto", "today", "") else raw_date

            version_raw = get_with_fallback(doc, "version", "1.0", "document")
            version = version_raw.replace(".", "_")

            output_formats = get_with_fallback(config_data, "output_format", ["md"], "root")
            if isinstance(output_formats, str):
                output_formats = [output_formats]

            document_meta = {
                "title": get_with_fallback(doc, "title", "📄 Documentation", "document"),
                "version": get_with_fallback(doc, "version", "1.0", "document"),
                "author": get_with_fallback(doc, "author", "Unknown", "document"),
                "date": date,
                "logoPath": resource_path(get_with_fallback(doc, "logoPath", "../generator/img/logo.svg", "document"), "assets/logo.svg"),
                "highlightTodo": get_with_fallback(doc, "highlightTodo", True, "document"),
                "showDocProgress": get_with_fallback(doc, "showDocProgress", True, "document")
            }

            return {
                "document": document_meta,
                "config_path": used_path,
                "source_dir": get_with_fallback(config_data, "source_dir", resource_path("../fileExamples", "./assets/fileExamples"), "root"),
                "recursive": bool(get_with_fallback(config_data, "recursive", True, "root")),
                "output_format": output_formats,
                "output_path": get_with_fallback(config_data, "output_path", f"./docs/Documentation_{version}", "root"),
                "backup_path": get_with_fallback(config_data, "backup_path", None, "root"),
                "readonly": get_with_fallback(config_data, "readonly", True, "root"),
                "headerCommentStyle": get_with_fallback(config_data, "headerCommentStyle", None, "root"),
            }, None
        except Exception as e:
            return None, f"[configSetup] Error parsing config file '{used_path}': {e}"

    # === Step 1: Try given config path ===
    result = try_load_and_parse(config_path)
    tried_default = (config_path == "")

    # === Step 2: Fallback to default path if needed ===
    if result is None and not tried_default:
        default_path = resource_path("../config.yaml", "assets/config.yaml")
        result = try_load_and_parse(default_path)

    if result is None:
        print("[configSetup] Failed to load and parse any config file.")

    return result, errors if errors else None

def resource_path(dev_path, prod_path=None):
    """
    Gibt den Pfad zur Ressource zurück – kompatibel für Entwicklung und PyInstaller (.exe).
    
    :param dev_path: Pfad zur Ressource während der Entwicklung (Fallback, wenn _MEIPASS NICHT verfügbar).
    :param prod_path: Produktivpfad zur Ressource (meist in assets folder).
    :return: Absoluter Pfad zur Ressource.
    """

    target_path = ""

    if hasattr(sys, "_MEIPASS"):
        # Im .exe-Modus: verwende mitgelieferte Ressourcen
        base_path = sys._MEIPASS
        target_path = prod_path if prod_path else dev_path
    else:
        # In der Entwicklungsumgebung
        base_path = os.path.dirname(os.path.abspath(__file__))
        target_path = dev_path

    return os.path.normpath(os.path.join(base_path, target_path))
