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

ui_file = os.path.join(os.path.dirname(__file__), '../ui/a_ward_params.ui')
UI_AWardParamsDialog, QtBaseClass = uic.loadUiType(ui_file)


class AWardParamsDialog(UI_AWardParamsDialog, QDialog):

    def __init__(self, parent):
        super(AWardParamsDialog, self).__init__(parent)
        self.setupUi(self)
        # radio_button_clusters_number
        self.radio_button_clusters_number.toggled.connect(self.update_cluster_number)
        self.radio_button_alpha_parameter.toggled.connect(self.update_alpha_parameter)


    def update_cluster_number(self):
        self.clusters_number_spin.setDisabled(not self.radio_button_clusters_number.isChecked())

    def update_alpha_parameter(self):
        self.alpha_parameter_spin.setDisabled(not self.radio_button_alpha_parameter.isChecked())

    @classmethod
    def ask(cls, parent):
        dialog = cls(parent)
        if dialog.exec_() == QDialog.Accepted:
            alpha = dialog.alpha_parameter_spin.value() if dialog.alpha_parameter_spin.isEnabled() else None
            return dialog.clusters_number_spin.value(), alpha
        raise BaseException("Rejected")
