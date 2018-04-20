import os
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from plot.plot import plot_svd
import matplotlib.pyplot as plt
from PyQt5 import QtGui

ui_file = os.path.join(os.path.dirname(__file__), '../ui/text_report.ui')
UI_TextReportDialog, QtBaseClass = uic.loadUiType(ui_file)


class TextReportDialog(UI_TextReportDialog, QDialog):
    def __init__(self, parent, report, selected_features):
        super(TextReportDialog, self).__init__(parent)
        self.setupUi(self)
        if report is None:
            self.text_browser.setText("Report is unavailable")
        else:
            self.text_browser.setText(report.text(selected_features))
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.text_browser.setFont(font)

    @classmethod
    def ask(cls, parent, report, selected_features):
        dialog = cls(parent, report, selected_features)
        if dialog.exec_() == QDialog.Accepted:
            return None
        return QDialog.Rejected
