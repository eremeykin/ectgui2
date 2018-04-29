import os

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from time import gmtime, strftime
from logging import Handler
from PyQt5.QtGui import *
import time

ui_file = os.path.join(os.path.dirname(__file__), '../ui/progress_dialog.ui')
UI_Progress, QtBaseClass = uic.loadUiType(ui_file)


class ProgressDialog(UI_Progress, QDialog):
    class ProgressThread(QThread):
        def __init__(self, function):
            super().__init__()
            self.function = function
            self.result = None

        def run(self):
            self.result = self.function()
            # return self.result

        def stop(self):
            self.terminate()

    def __init__(self, parent, progress, function, autofininsh=False):
        super(ProgressDialog, self).__init__(parent)
        self.function = function
        self.setupUi(self)
        self.progress = progress
        self.progress_thread = ProgressDialog.ProgressThread(self.function)
        self.progress_bar.setRange(0, 0)
        self.progress_thread.finished.connect(self.finish)
        self.autofininsh = autofininsh
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.force_stop)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # trigger every sec
        self.time_passed = 0
        self.label.setText(str(progress))
        current_time = strftime("%H:%M:%S", time.localtime())
        self.label_started_at.setText("Started at: {}".format(current_time))
        if autofininsh:
            layout = self.layout()
            layout.removeWidget(self.button_box)
            self.button_box.deleteLater()
            self.button_box = None
        self.finished_actions = []
        self.cancelled_actions = []
        self.cancelled = False
        self.logger = ProgressLogHandler()
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.text_browser.setFont(font)

    def update_time(self):
        self.time_passed += 1
        hours = self.time_passed // (60 ** 2)
        mins = (self.time_passed - hours * (60 ** 2)) // 60
        secs = self.time_passed - hours * (60 ** 2) - mins * 60
        self.label_time_passed.setText("Time passed: {:3d}:{:02d}:{:02d}".format(hours, mins, secs))
        self.text_browser.setPlainText("\n".join([x for x in self.logger.get]))
        if self.time_passed > 2 and self.autofininsh:
            self.show()

    def finish(self):
        self.timer.timeout.disconnect()
        self.logger.stop()
        self.text_browser.setPlainText("\n".join([x for x in self.logger.get]))
        if self.autofininsh:
            self.hide()
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        if not self.cancelled:
            for action in self.finished_actions:
                action()

    def run(self):
        self.progress_thread.start()
        self.logger.start()
        if not self.autofininsh:
            self.show()

    def after_finished(self, action):
        self.finished_actions.append(action)

    def after_cancelled(self, action):
        self.cancelled_actions.append(action)

    def force_stop(self):
        self.cancelled = True
        self.logger.stop()
        self.progress_thread.stop()
        self.progress_thread.wait()
        for action in self.cancelled_actions:
            action()

    def get_result(self):
        return self.progress_thread.result


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


class ProgressLogHandler(Handler, metaclass=Singleton):
    def __init__(self):
        super(ProgressLogHandler, self).__init__()
        self._collected = []
        self._start = False

    @property
    def get(self):
        return self._collected

    def emit(self, record):
        self.format(record)
        if self._start:
            self._collected.append(self.fmt(record))

    def start(self):
        self._collected = []
        self._start = True

    def stop(self):
        self._start = False

    def fmt(self, msg):
        if hasattr(msg, "asctime"):
            return "{}.{:03d} [{}] - {}".format(msg.asctime, int(msg.msecs), msg.levelname, msg.getMessage())
        else:
            return "corrupted"
