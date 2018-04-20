import os

from PyQt5 import uic
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

ui_file = os.path.join(os.path.dirname(__file__), '../ui/hist.ui')
UI_HistDialog, QtBaseClass = uic.loadUiType(ui_file)


class HistDialog(UI_HistDialog, QDialog):
    def __init__(self, parent, feature):
        super(HistDialog, self).__init__(parent)
        self.setupUi(self)
        self.feature = feature
        self.parent = parent
        self.figure = Figure()
        self.plot = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.plot, self)
        self.gridLayout.addWidget(self.plot)
        self.gridLayout.addWidget(self.toolbar)
        self.spin_box.valueChanged.connect(self.update)
        self.ax = self.figure.add_subplot(111)
        self.ax.clear()
        self.plot.draw()
        self.update()

    def update(self):
        self.ax.cla()
        self.ax.hist(self.feature.series, bins=self.spin_box.value())
        self.plot.draw()

    @classmethod
    def ask(cls, parent, feature):
        dialog = cls(parent, feature)
        if dialog.exec_() == QDialog.Accepted:
            return None
        return QDialog.Rejected
