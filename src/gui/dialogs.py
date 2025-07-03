# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

"""
Application specific content window for
help/changelog view in new window instance.
"""

import os

from configSetup.installModules import ensure_modules
from configSetup.configSetup import resource_path
from streamLogger.log_setup import logger

ensure_modules([("PyQt5", "PyQt5")])

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout,
    QDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
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

        self.icon_path = resource_path("../utils/icon/icon.ico", "assets/icon.ico")
        print(f"Icon Path: {self.icon_path}")
        if os.path.exists(self.icon_path):
            self.setWindowIcon(QIcon(self.icon_path))
        else:
            logger.log(f"Icon Path can't be found: {self.icon_path}", "warning")

        layout = QVBoxLayout(self)
        layout.addWidget(content_widget)
