import os
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from tables.models.pandas_model import PandasTableModel
from matplotlib.figure import Figure
from plot.plot import plot_svd
import pandas as pd
import numpy as np
from PyQt5 import QtGui
from PyQt5 import QtCore

ui_file = os.path.join(os.path.dirname(__file__), '../ui/table_report.ui')
UI_TableDialog, QtBaseClass = uic.loadUiType(ui_file)


class TableDialog(UI_TableDialog, QDialog):
    def __init__(self, parent, report):
        super(TableDialog, self).__init__(parent)
        self.setupUi(self)
        if report is None:
            return
        model = ReportTableModel(report)
        self.table_view.setModel(model)

    @classmethod
    def ask(cls, parent, report):
        dialog = cls(parent, report)
        if dialog.exec_() == QDialog.Accepted:
            return None
        return QDialog.Rejected


class ReportTableModel(PandasTableModel):
    def __init__(self, report):
        index = [f.name for f in report.norm_features]
        df = pd.DataFrame(columns=index)
        self.counts = []
        for cluster in report.cluster_structure.clusters:
            self.counts.append(cluster.power)
            s = pd.Series(report.r_norm.apply(cluster.centroid), index=index)
            df = df.append(s, ignore_index=True)
        super(ReportTableModel, self).__init__(df)
        data = np.array([f.series for f in report.norm_features]).T
        self.means = data.mean(axis=0)
        self.report = report

    def rowCount(self, parent=QtCore.QModelIndex(), *args, **kwargs):
        return self.df.shape[0] + 1

    def columnCount(self, parent=QtCore.QModelIndex(), *args, **kwargs):
        return self.df.shape[1] + 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        i = index.row()
        j = index.column()
        if role == QtCore.Qt.DisplayRole:
            if j == self.columnCount() - 1 and i == self.rowCount() - 1:
                return '{0}'.format(sum(self.counts))
            if j == self.columnCount() - 1:
                return '{0}'.format(self.counts[i])
            if i == self.rowCount() - 1:
                return '{0:.3f}'.format(self.means[j])
            return '{0:.3f}'.format(self.df.iat[i, j])
        if role == QtCore.Qt.BackgroundColorRole:
            return self.color(i, j)
        else:
            return QtCore.QVariant()

    def color(self, i, j):
        try:
            value = (self.df.iat[i, j] - self.means[j]) / self.means[j]
            if value > self.report.THRESHOLD:
                return QtCore.QVariant(QtGui.QColor(255, 90, 90))
            if -value > self.report.THRESHOLD:
                return QtCore.QVariant(QtGui.QColor(0, 191, 255))
        except IndexError:
            return QtCore.QVariant()

    def headerData(self, col, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if col == self.columnCount() - 1:
                return QtCore.QVariant("Entities")
            c_name = self.df.columns.values[col]
            return QtCore.QVariant(c_name)
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            if col == self.rowCount() - 1:
                return QtCore.QVariant("Mean")
            return QtCore.QVariant(str(self.df.index.values[col]))
        return QtCore.QVariant()
