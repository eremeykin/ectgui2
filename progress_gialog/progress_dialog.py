import os

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from time import gmtime, strftime

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
            return self.result

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
        current_time = strftime("%H:%M:%S", gmtime())
        self.label_started_at.setText("Started at: {}".format(current_time))
        if autofininsh:
            layout = self.layout()
            layout.removeWidget(self.button_box)
            self.button_box.deleteLater()
            self.button_box = None
        self.finished_actions = []
        self.cancelled_actions = []
        self.cancelled = False

    def update_time(self):
        self.time_passed += 1
        hours = self.time_passed // (60 ** 2)
        mins = (self.time_passed - hours * (60 ** 2)) // 60
        secs = self.time_passed - hours * (60 ** 2) - mins * 60
        self.label_time_passed.setText("Time passed: {:3d}:{:02d}:{:02d}".format(hours, mins, secs))

    def finish(self):
        self.timer.timeout.disconnect()
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
        self.show()
        self.progress_thread.start()

    def after_finished(self, action):
        self.finished_actions.append(action)

    def after_cancelled(self, action):
        self.cancelled_actions.append(action)

    def force_stop(self):
        self.cancelled = True
        self.progress_thread.terminate()
        for action in self.cancelled_actions:
            action()

    def get_result(self):
        return self.progress_thread.result
