# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

"""
Application specific content window for
help/changelog view in new window instance.
"""

import os
from typing import Optional

from configSetup.installModules import ensure_modules
from configSetup.configSetup import resource_path
from streamLogger.log_setup import logger

ensure_modules([("PyQt5", "PyQt5")])

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout,
    QDialog, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

def show_user_prompt(self, text: str, title: str = "Info", level: str = "info",
                     icon_path: Optional[str] = None,
                     buttons: Optional[QMessageBox.StandardButtons] = None,
                     default_button: Optional[QMessageBox.StandardButton] = None) -> QMessageBox.StandardButton:
    """
    Displays a standardized message box with logging.
    - level: "info", "warning", or "error"
    """

    icon_map = {
        "info": QMessageBox.Information,
        "warning": QMessageBox.Warning,
        "error": QMessageBox.Critical
    }

    # Fallback messagebox to "info"
    icon = icon_map.get(level.lower(), QMessageBox.Information)

    logger.log(f"{text}", f"{level}")

    box = QMessageBox()
    box.setIcon(icon)
    box.setWindowTitle(title)
    if icon_path and os.path.exists(icon_path):
        box.setWindowIcon(QIcon(icon_path))
    box.setText(text)

    if buttons is not None:
        box.setStandardButtons(buttons)
        if default_button is not None:
            box.setDefaultButton(default_button)

    return box.exec()

def resolve_window_icon(primary: str, fallback: str) -> Optional[str]:
    """
    Resolves a valid QIcon path from the given resource path.
    Logs a warning if icon-path not found.
    """
    icon_path = resource_path(primary, fallback)
    if os.path.exists(icon_path):
        print(f"Icon Path: {icon_path}")
        return icon_path
    logger.log(f"Icon Path can't be found: {icon_path}", "warning")
    return None

class ContentDialogWindow(QDialog):
    """
    class, to setup specific content-window-instance.
    """
    def __init__(self, content_widget:
                 QWidget, title: str, size: tuple = (800, 600), parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(*size)

        # "?"-Button oben rechts entfernen
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.icon_path = resolve_window_icon("../utils/icon/icon.ico", "assets/icon.ico")
        if self.icon_path:
            self.setWindowIcon(QIcon(self.icon_path))

        layout = QVBoxLayout(self)
        layout.addWidget(content_widget)
