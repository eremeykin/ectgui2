import os
import sys

import pandas as pd
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from norm_settings.norm_settings import NormSettingDialog
from normalization import Normalization
from tables.models.norm import *
from tables.raw_table import RawTable
from tables.norm_table import NormTable

ui_file = os.path.join(os.path.dirname(__file__), 'ui/main2.ui')
ui_file_norm_settings = os.path.join(os.path.dirname(__file__), 'ui/norm_settings.ui')

UI_ECT, QtBaseClass = uic.loadUiType(ui_file)


class ECT(UI_ECT, QMainWindow):
    parse_triggered = pyqtSignal()

    class LoadDataThread(QThread):

        def __init__(self, data_file):
            super().__init__()
            self.data_file = data_file
            self.data = None

        def run(self):
            self.data = pd.read_csv(self.data_file)

    def __init__(self, parent=None):
        super(ECT, self).__init__(parent)
        self.setupUi(self)
        # load settings
        self.qt_settings = QSettings('ECT', 'hse')
        # bind actions
        self.action_open.triggered.connect(self.open)
        self.action_exit.triggered.connect(sys.exit)
        self.action_settings.triggered.connect(self.settings)
        self.action_normalize.setChecked(self.qt_settings.value("NormEnabled", type=bool))
        self.action_normalize.triggered.connect(self.normalize)
        self.raw_table = RawTable(self.table_view_raw, self)
        self.norm_table = NormTable(self.table_view_norm, self)
        self.load_thread = None

        self.statusBar().showMessage('Ready')

    def open(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file', '\home')[0]
        if not file_name:
            return
        self.load_thread = ECT.LoadDataThread(file_name)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self._set_status("Loading data: {} ...".format(file_name))
        self.load_thread.finished.connect(lambda: self.raw_table.set_data(self.load_thread.data))
        self.load_thread.finished.connect(lambda: self._set_status("Ready"))
        self.load_thread.finished.connect(lambda: QApplication.restoreOverrideCursor())
        self.load_thread.start()

    def _set_status(self, status):
        self.statusBar().showMessage(status)

    def settings(self):
        try:
            enabled, center, range_ = NormSettingDialog.ask(self)
            self.qt_settings.setValue("NormEnabled", enabled)
            self.qt_settings.setValue('Center', center)
            self.qt_settings.setValue('Range', range_)
            self.action_normalize.setChecked(enabled)
            self.norm_table.update_norm()
        except BaseException:  # Dialog Rejected
            pass

    def normalize(self):
        self.qt_settings.setValue("NormEnabled", self.action_normalize.isChecked())
        self.norm_table.update_norm()

    def normalize_column(self, series):
        self.norm_table.add_column(series)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = ECT()
    widget.show()
    sys.exit(app.exec_())
