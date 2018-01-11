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

ui_file = os.path.join(os.path.dirname(__file__), '../ui/auto_choose_p.ui')
UI_AutoChoosePDialog, QtBaseClass = uic.loadUiType(ui_file)


class AutoChoosePDialog(UI_AutoChoosePDialog, QDialog):
    def __init__(self, parent):
        super(AutoChoosePDialog, self).__init__(parent)
        self.setupUi(self)
        self.clusters_number_spin.setValue(parent.clusters_number_spin.value())

    @classmethod
    def ask(cls, parent):
        dialog = cls(parent)
        if dialog.exec_() == QDialog.Accepted:
            start = float(dialog.start_spin.value())
            step = float(dialog.step_spin.value())
            end = float(dialog.end_spin.value())
            times_to_run = int(dialog.times_spin.value())
            criterion = dialog.criterion_combo_box.currentText()
            clusters_number = int(dialog.clusters_number_spin.value())
            return start, step, end, times_to_run, criterion, clusters_number
        raise BaseException("Rejected")
