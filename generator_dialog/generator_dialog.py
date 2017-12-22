import os

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5 import QtGui

ui_file = os.path.join(os.path.dirname(__file__), '../ui/generator.ui')
UI_GeneratorDialog, QtBaseClass = uic.loadUiType(ui_file)


class GeneratorDialog(UI_GeneratorDialog, QDialog):
    def __init__(self, parent):
        super(GeneratorDialog, self).__init__(parent)
        self.setupUi(self)

        self.figure = Figure()
        self.plot = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.plot, self)
        self.gridLayout.addWidget(self.plot)
        self.gridLayout.addWidget(self.toolbar)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.plot.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.generator_seed_line_edit.textChanged.connect(self.update)
        self.minimal_cluster_cardinality_line_edit.textChanged.connect(self.update)
        self.number_of_clusters_line_edit.textChanged.connect(self.update)
        self.number_of_objects_line_edit.textChanged.connect(self.update)
        self.features_line_edit.textChanged.connect(self.update)
        self.box_parameter_spin.valueChanged.connect(self.update)
        self.buttonBox.buttons()[0].setDisabled(True)

        import numpy as np
        # data = np.random.randint(0, 10, (300, 2))
        # data = np.random.normal(0, 4, size=(300, 2))
        # data = data.astype(float)
        # print(data)
        self.ax = self.figure.add_subplot(111)
        self.ax.clear()
        # ax.scatter(data[:, 0], data[:, 1])
        self.plot.draw()

    def update(self):
        import numpy as np

        seed = self.generator_seed_line_edit.text()
        np.random.seed(int(seed))
        cardinality = self.minimal_cluster_cardinality_line_edit.text()
        n_clusters = self.number_of_clusters_line_edit.text()
        features = self.features_line_edit.text()
        objects = self.number_of_objects_line_edit.text()
        a = self.box_parameter_spin.text().replace(',', '.')
        import numpy as np
        from generators.kovaleva import kovaleva
        data, labels = kovaleva(int(cardinality), int(n_clusters), (int(objects), int(features)), float(a))
        self.buttonBox.buttons()[0].setDisabled(False)
        self.ax.cla()
        self.ax.scatter(data[:, 0], data[:, 1])
        self.plot.draw()



    @classmethod
    def ask(cls, parent):
        dialog = cls(parent)
        if dialog.exec_() == QDialog.Accepted:
            return None
        raise BaseException("Rejected")
