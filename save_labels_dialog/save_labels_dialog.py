import os

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

ui_file = os.path.join(os.path.dirname(__file__), '../ui/save_labels.ui')
UI_SaveLabels, QtBaseClass = uic.loadUiType(ui_file)


class SaveLabelsDialog(UI_SaveLabels, QDialog):
    def __init__(self, parent):
        super(SaveLabelsDialog, self).__init__(parent)
        self.setupUi(self)
        self.tool_button.clicked.connect(self.file_dialog)
        self.separately_radio_button.toggled.connect(self.update)
        self.yes_radio_button.toggled.connect(self.update)
        self.no_radio_button.toggled.connect(self.update)

    def update(self):
        self.tool_button.setEnabled(False)
        self.line_edit.setEnabled(False)
        if self.separately_radio_button.isChecked():
            self.tool_button.setEnabled(True)
            self.line_edit.setEnabled(True)

    def file_dialog(self):
        file_name = QFileDialog.getSaveFileName(self, 'Open file', 'labels.lbs')[0]
        if not file_name:
            return
        self.line_edit.setText(file_name)

    @classmethod
    def ask(cls, parent):
        dialog = cls(parent)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.yes_radio_button.isChecked():
                return "Yes", None
            if dialog.no_radio_button.isChecked():
                return "No", None
            if dialog.separately_radio_button.isChecked():
                return "Separately", dialog.line_edit.text()
        return QDialog.Rejected
