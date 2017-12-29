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

ui_file = os.path.join(os.path.dirname(__file__), '../ui/generator.ui')
UI_GeneratorDialog, QtBaseClass = uic.loadUiType(ui_file)


class GeneratorDialog(UI_GeneratorDialog, QDialog):
    def __init__(self, parent):
        super(GeneratorDialog, self).__init__(parent)
        self.setupUi(self)

        self.parent = parent
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

        self.generator_seed_spin.setValue(self.parent.qt_settings.value("GeneratorDialog-GeneratorSeed", type=int))
        self.minimal_cluster_cardinality_spin.setValue(
            self.parent.qt_settings.value("GeneratorDialog-MinimalClusterCardinality", type=int))
        self.number_of_clusters_spin.setValue(
            self.parent.qt_settings.value("GeneratorDialog-NumberOfClusters", type=int))
        self.features_spin.setValue(self.parent.qt_settings.value("GeneratorDialog-Features", type=int))
        self.number_of_objects_spin.setValue(self.parent.qt_settings.value("GeneratorDialog-NumberOfObjects", type=int))
        self.box_parameter_spin.setValue(self.parent.qt_settings.value("GeneratorDialog-BoxParameter", type=float))

        self.generator_seed_spin.valueChanged.connect(self.update)
        self.minimal_cluster_cardinality_spin.valueChanged.connect(self.update)
        self.number_of_clusters_spin.valueChanged.connect(self.update)
        self.number_of_objects_spin.valueChanged.connect(self.update)
        self.features_spin.valueChanged.connect(self.update)
        self.box_parameter_spin.valueChanged.connect(self.update)
        self.buttonBox.buttons()[0].setDisabled(True)

        self.ax = self.figure.add_subplot(111)
        self.ax.clear()
        self.plot.draw()
        self.data = None
        self.labels = None
        self.update()

    def update(self):
        import numpy as np

        seed = self.generator_seed_spin.text()
        np.random.seed(int(seed))
        cardinality = int(self.minimal_cluster_cardinality_spin.text())
        n_clusters = int(self.number_of_clusters_spin.text())
        features = int(self.features_spin.text())
        n_objects = int(self.number_of_objects_spin.text())
        a = float(self.box_parameter_spin.text().replace(',', '.'))

        self.parent.qt_settings.setValue("GeneratorDialog-GeneratorSeed", seed)
        self.parent.qt_settings.setValue("GeneratorDialog-MinimalClusterCardinality", cardinality)
        self.parent.qt_settings.setValue("GeneratorDialog-NumberOfClusters", n_clusters)
        self.parent.qt_settings.setValue("GeneratorDialog-Features", features)
        self.parent.qt_settings.setValue("GeneratorDialog-NumberOfObjects", n_objects)
        self.parent.qt_settings.setValue("GeneratorDialog-BoxParameter", a)

        # residue = n_objects - n_clusters * cardinality
        self.minimal_cluster_cardinality_spin.setMaximum(n_objects // n_clusters)
        self.number_of_clusters_spin.setMaximum(n_objects // cardinality)
        self.number_of_objects_spin.setMinimum(n_clusters * cardinality)

        from generators.kovaleva import kovaleva
        self.ax.cla()
        try:
            self.data, self.labels = kovaleva(cardinality, n_clusters, (n_objects, features), a)
            self.buttonBox.buttons()[0].setDisabled(False)
            plot_svd(self.ax, self.data, self.labels, "SVD diagram of generated data")
            # self.ax.scatter(data[:, 0], data[:, 1])
        except ValueError:
            self.ax.text(0.5, 0.5, 'Sorry, unknown error.', horizontalalignment='center',
                         verticalalignment='center',
                         transform=self.ax.transAxes, fontsize=18)
        self.plot.draw()

    @classmethod
    def ask(cls, parent):
        dialog = cls(parent)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.data, dialog.labels
        raise BaseException("Rejected")
