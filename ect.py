from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys
from models.raw import *
import pandas as pd
import os
from norm_settings.norm_settings import NormSettingDialog
from normalization import Normalization

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

    def __init__(self, parent=None, name=None):
        super(ECT, self).__init__(parent)
        self.setupUi(self)
        self.actionOpen.triggered.connect(self.action_open)
        self.actionExit.triggered.connect(sys.exit)
        self.actionSettings.triggered.connect(self.action_settings)
        self.actionNormalize.triggered.connect(self.action_normalize)
        self.statusBar().showMessage('Ready')
        self._raw_data = None
        self._data = None
        self.load_thread = None
        self.settings = QSettings('ECT', 'hse')

    def action_open(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file', '\home')[0]
        if not file_name:
            return
        self.load_thread = ECT.LoadDataThread(file_name)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self._set_status("Loading data: {} ...".format(file_name))
        self.load_thread.finished.connect(self._get_data_from_thread)
        self.load_thread.finished.connect(self.update_table)
        self.load_thread.finished.connect(lambda: self._set_status("Ready"))
        self.load_thread.finished.connect(lambda: QApplication.restoreOverrideCursor())
        self.load_thread.start()

    def _set_status(self, status):
        self.statusBar().showMessage(status)

    def _get_data_from_thread(self):
        self._raw_data = self.load_thread.data
        if self.actionSettings.isChecked():
            self.action_normalize()
        else:
            self._data = self._raw_data

    def update_table(self):
        model = RawTableModel(self._data)
        self.tableView.setModel(model)

    def action_settings(self):
        print("Open")
        d = NormSettingDialog(self)
        d.open()

    def action_normalize(self):
        print("apply")
        norm = Normalization('Mean', 'Semi range')
        self._data = norm.apply(self._raw_data)
        self.update_table()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = ECT()
    widget.show()
    sys.exit(app.exec_())
