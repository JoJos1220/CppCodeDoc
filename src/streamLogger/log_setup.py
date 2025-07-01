# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import os, logging
from logging.handlers import TimedRotatingFileHandler
from PyQt5.QtCore import QTimer

class TimedSizedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='midnight', interval=1, backup_count=12,
                 encoding=None, delay=False, utc=False, max_bytes=0):
        super().__init__(filename, when, interval, backup_count,
                         encoding=encoding, delay=delay, utc=utc)
        self.max_bytes = max_bytes

    def shouldRollover(self, record):
        if super().shouldRollover(record):
            return 1
        if self.max_bytes > 0:
            self.stream = self.stream or self._open()
            self.stream.seek(0, os.SEEK_END)
            if self.stream.tell() >= self.max_bytes:
                return 1
        return 0

class StreamLogger:
    def __init__(self):
        self.app_class = None

    def set_app_class(self, app_class):
        self.app_class = app_class

    def log(self, message, level="info"):
        getattr(logging, level)(message)
        print("[LOG] " + message)
        if hasattr(self.app_class, "instance") and self.app_class.instance:
            QTimer.singleShot(0, lambda: self.app_class.instance.append_log(message))

    def setup_logging(self, log_name = "log.log", log_dir=os.path.join(os.path.dirname(__file__), "..\\log")):
        # Setup and check logging directory
        log_file_path = os.path.join(log_dir, log_name)

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 1MB max, monatliche Rotation, max. 6 Backups
        handler = TimedSizedRotatingFileHandler(
            log_file_path, when="midnight", interval=1, backup_count=0, max_bytes=1*1024*1024, encoding="utf-8"
        )
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

# singleTon Class instance to globally ensure usage within project
logger = StreamLogger()
