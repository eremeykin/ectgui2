from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import *
class StatusBar:

    def __init__(self, parent):
        self.parent = parent
        self.status_bar = parent.statusBar()
        self.status_msg = ""
        # status label
        self.status_label = QLabel("")
        self.status_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.status_label.setMinimumWidth(10)
        # normalization label
        self.normalization_label = QLabel("")
        self.normalization_label.setMinimumWidth(10)
        self.normalization_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        # result label
        self.result_label = QLabel("")
        self.result_label.setMinimumWidth(10)
        self.result_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        # add widgets
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addWidget(self.normalization_label)
        self.status_bar.addWidget(self.result_label)

    def status(self, status_msg=None):
        if status_msg is not None:
            self.status_msg = "Ready"
            # status_msg = self.status_bar.currentMessage()
        enabled = self.parent.app_settings.norm_enabled
        enabled = "enabled" if enabled else "disabled"
        center = self.parent.app_settings.center
        spread = self.parent.app_settings.spread
        power = self.parent.app_settings.power
        norm_str = "Normalization: {}, center: {}, spread: {}".format(enabled, center, spread)
        if power is not None and power != "":
            norm_str += ", mink power: {:8.4}".format(power)
        self.status_label.setText("Status: {}.".format(status_msg))
        self.normalization_label.setText(norm_str + ".")
        report = self.parent.report
        if report is None:
            self.result_label.setText("Result: not available".format())
        else:
            self.result_label.setText("Result: ({:.3} s) {}".format(report.time, report.algorithm))


