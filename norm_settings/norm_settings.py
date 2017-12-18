import os

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

ui_file = os.path.join(os.path.dirname(__file__), '../ui/norm_settings.ui')
UI_NormSettings, QtBaseClass = uic.loadUiType(ui_file)


class NormSettingDialog(UI_NormSettings, QDialog):
    def __init__(self, parent):
        super(NormSettingDialog, self).__init__(parent)
        self.setupUi(self)
        settings = QSettings('ECT', 'hse')
        enabled = settings.value('NormEnabled', type=bool)
        center = settings.value('Center', type=str)
        range_ = settings.value('Range', type=str)
        self.norm_enabled.setChecked(enabled)
        center_index = self.combo_box_center.findText(center)
        range_index = self.combo_box_range.findText(range_)
        self.combo_box_center.setCurrentIndex(center_index)
        self.combo_box_range.setCurrentIndex(range_index)

    @property
    def enabled(self):
        return self.norm_enabled.isChecked()

    @property
    def center(self):
        return self.combo_box_center.currentText()

    @property
    def range(self):
        return self.combo_box_range.currentText()

    @classmethod
    def ask(cls, parent):
        dialog = cls(parent)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.enabled, dialog.center, dialog.range
        raise BaseException("Rejected")
