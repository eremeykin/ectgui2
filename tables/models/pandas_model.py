from PyQt5 import QtGui
from PyQt5.QtGui import QColor
from PyQt5 import QtCore
import pandas as pd


class PandasTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data=pd.DataFrame()):
        super(PandasTableModel, self).__init__()
        self.df = data

    def rowCount(self, parent=QtCore.QModelIndex(), *args, **kwargs):
        return self.df.shape[0]

    def columnCount(self, parent=QtCore.QModelIndex(), *args, **kwargs):
        if len(self.df.shape) > 1:
            return self.df.shape[1]
        if self.df.shape[0] == 0:
            return 1
        return 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        i = index.row()
        j = index.column()
        if role == QtCore.Qt.DisplayRole:
            return '{0}'.format(self.df.iat[i, j])
        if role == QtCore.Qt.BackgroundColorRole:
            return self.color(i, j)
        else:
            return QtCore.QVariant()

    def color(self, i, j):
        return QtCore.QVariant()

    def headerData(self, col, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            c_name = self.df.columns.values[col]
            return QtCore.QVariant(str(c_name))
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(str(self.df.index.values[col]))
        return QtCore.QVariant()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled
