# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import os, sys, logging, tempfile, shutil, pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.streamLogger.log_setup import StreamLogger

@pytest.fixture
def temp_log_dir():
    """Creats a temp directory during pytests, and cleansup if it is finished."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def stream_logger():
    """creates a clean StreamLogger Instance for each test and ensures no dependancys
    to previoous executed tests. This is important for the log file creation."""
    logger = StreamLogger()
    yield logger
    logging.shutdown()

# Pytest if log file is created and contains the log message
def test_log_file_creation(temp_log_dir, stream_logger):
    log_name = "test.log"
    log_dir = os.path.join(temp_log_dir, "log")
    full_log_path = os.path.join(log_dir, log_name)
    print(f"Log path: {full_log_path}")

    stream_logger.setup_logging(log_name=log_name, log_dir=log_dir)
    stream_logger.log("Test message", level="info")

    assert os.path.exists(full_log_path)
    with open(full_log_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Test message" in content

# check if gui callback is called by timer singleshot
def test_gui_callback_called(stream_logger):
    """
     This test ensures, that the "append_log" function is called by an overloaded
     class instance. This must be ensured, because by append_log the GUI is updated
     and the logging window shows the latest log inputs!.
    """
    mock_instance = MagicMock()
    mock_instance.append_log = MagicMock()

    class DummyApp:
        instance = mock_instance

    stream_logger.set_app_class(DummyApp)

    # QTimer.singleShot mock, for simulation of direct function call
    with patch("src.streamLogger.log_setup.QTimer.singleShot", lambda ms, func: func()):
        stream_logger.log("Test GUI log", level="debug")
        mock_instance.append_log.assert_called_once_with("Test GUI log")

# Test if log rollsover if a specific size is reached
def test_log_rollover_due_to_size(stream_logger, temp_log_dir):
    """
     This test ensures, that a log_rollover happens if a specific file size exceeds!.
    """
    log_name = "rollover_test.log"
    log_dir = os.path.join(temp_log_dir, "log")

    stream_logger.setup_logging(log_name=log_name, log_dir=log_dir)

    # Write a lot of log messages to release a rollover
    message = "A" * 1024  # 1024
    for _ in range(1024 + 1):   # should be ~ 1 048 576 bytes > 1MB is default
        stream_logger.log(message)

    # close log and check if rollover happend
    logging.shutdown()

    log_files = os.listdir(log_dir)
    print("Log files:", log_files)

    # e.g. results: ["rollover_test.log", "rollover_test.log.1"]
    rolled_over = any(f != log_name and f.startswith(log_name) for f in log_files)
    assert rolled_over, "Expected a rollover log file, but none found."