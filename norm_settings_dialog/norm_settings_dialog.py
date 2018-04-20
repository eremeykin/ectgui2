import os

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from settings import Settings

ui_file = os.path.join(os.path.dirname(__file__), '../ui/norm_settings.ui')
UI_NormSettings, QtBaseClass = uic.loadUiType(ui_file)


class NormSettingDialog(UI_NormSettings, QDialog):
    def __init__(self, parent):
        super(NormSettingDialog, self).__init__(parent)
        self.setupUi(self)
        app_settings = Settings()
        self.norm_enabled.setChecked(app_settings.norm_enabled)
        center_index = self.combo_box_center.findText(app_settings.center)
        spread_index = self.combo_box_spread.findText(app_settings.spread)
        self.combo_box_center.setCurrentIndex(center_index)
        self.combo_box_center.currentIndexChanged.connect(self.enable_pow)
        self.combo_box_spread.setCurrentIndex(spread_index)
        try:
            self.spin_box_power.setValue(float(app_settings.power))
        except ValueError:
            self.spin_box_power.setValue(2.0)
        self.enable_pow()

    def enable_pow(self):
        self.spin_box_power.setDisabled(not "Mink" in self.combo_box_center.currentText())

    @property
    def enabled(self):
        return self.norm_enabled.isChecked()

    @property
    def center(self):
        return self.combo_box_center.currentText()

    @property
    def spread(self):
        return self.combo_box_spread.currentText()

    @property
    def power(self):
        return float(self.spin_box_power.value())

    @classmethod
    def ask(cls, parent):
        dialog = cls(parent)
        if dialog.exec_() == QDialog.Accepted:
            power = dialog.power if dialog.spin_box_power.isEnabled() else None
            return dialog.enabled, dialog.center, dialog.spread, power
        raise BaseException("Rejected")
