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
ui_file = os.path.join(os.path.dirname(__file__), '../ui/a_ward_pb_params.ui')
UI_AWardPBParamsDialog, QtBaseClass = uic.loadUiType(ui_file)


class AWardPBParamsDialog(UI_AWardPBParamsDialog, QDialog):
    def __init__(self, parent):
        super(AWardPBParamsDialog, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        # self.tool_button.clicked.connect(lambda: self.parent.auto_choose_p(self))

    def reject(self):
        self.hide()

    @classmethod
    def ask(cls, parent):
        dialog = cls(parent)
        res = dialog.exec_()
        if res == QDialog.Accepted:
            return int(dialog.clusters_number_spin.value()), \
                   float(dialog.minkowski_power_spin.value()), \
                   float(dialog.parameter_spin.value()), \
                   int(dialog.threshold_spin_box.value())
        return QDialog.Rejected
