# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os
import pytest
from unittest.mock import patch
from PyQt5.QtWidgets import QLabel, QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.gui.dialogs import ContentDialogWindow, resolve_window_icon


def test_resolve_window_icon_path_exists(tmp_path):
    # Temp Dummy-file
    icon_file = tmp_path / "icon.ico"
    icon_file.write_text("dummy icon data")

    # resource_path should return dummy-path
    with patch("src.gui.dialogs.resource_path", return_value=str(icon_file.resolve())), \
        patch("src.gui.dialogs.logger") as mock_logger:
        result = resolve_window_icon("unused_primary", "unused_fallback")
        assert result == str(icon_file.resolve())
        mock_logger.log.assert_not_called()


def test_resolve_window_icon_path_missing(tmp_path):
    missing_file = tmp_path / "missing.ico"

    # resource_path should return none
    with patch("src.gui.dialogs.resource_path", return_value=str(missing_file)), \
         patch("src.gui.dialogs.logger") as mock_logger:
        result = resolve_window_icon("unused_primary", "unused_fallback")
        assert result is None
        mock_logger.log.assert_called_once()
        args, _ = mock_logger.log.call_args
        assert "can't be found" in args[0]
        assert args[1] == "warning"

# skipping test if no display is available!(e.g. in act or Xvfb environment)
@pytest.mark.skipif(
    not os.environ.get("DISPLAY"),
    reason="Skipping GUI test: DISPLAY not available (headless or act environment)"
)
def test_dialog_creates_window():
    app = QApplication(sys.argv)
    content = QLabel("ContentDialogWindow")
    dialog = ContentDialogWindow(content_widget=content, title="TestWindow", size=(400, 300))

    assert dialog.windowTitle() == "TestWindow"
    assert dialog.width() == 400
    assert dialog.height() == 300
    assert dialog.layout().count() == 1
    assert dialog.layout().itemAt(0).widget().text() == "ContentDialogWindow"
    app.quit()
