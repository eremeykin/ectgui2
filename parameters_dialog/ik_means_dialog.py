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

ui_file = os.path.join(os.path.dirname(__file__), '../ui/ik_means_params.ui')
UI_IKMeansParamsDialog, QtBaseClass = uic.loadUiType(ui_file)


class IKMeansParamsDialog(UI_IKMeansParamsDialog, QDialog):

    def __init__(self, parent):
        super(IKMeansParamsDialog, self).__init__(parent)
        self.setupUi(self)

    @classmethod
    def ask(cls, parent):
        dialog = cls(parent)
        if dialog.exec_() == QDialog.Accepted:
            return int(dialog.threshold_spin_box.value())
        return QDialog.Rejected
