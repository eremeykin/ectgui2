from PyQt5 import QtGui
from PyQt5.QtGui import QColor

__author__ = 'eremeykin'
import pandas as pd
from PyQt5 import QtCore


class FeaturesTableModel(QtCore.QAbstractTableModel):
    def __init__(self, features=None):
        super(FeaturesTableModel, self).__init__()
        self.features = features if features is not None else []

    def rowCount(self, QModelIndex_parent=QtCore.QModelIndex(), *args, **kwargs):
        return len(self.features[0])

    def columnCount(self, QModelIndex_parent=QtCore.QModelIndex(), *args, **kwargs):
        return len(self.features)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        i = index.row()
        j = index.column()
        if role == QtCore.Qt.DisplayRole:
            return '{0}'.format(self.features[j][i])
        if role == QtCore.Qt.BackgroundColorRole:
            return self.color_injection(i, j)
        else:
            return QtCore.QVariant()

    def color_injection(self, i, j):
        return QtCore.QVariant()

    def headerData(self, p_int, Qt_Orientation, int_role=None):
        if len(self.features) == 0:
            return QtCore.QVariant()
        if Qt_Orientation == QtCore.Qt.Horizontal and int_role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.features[p_int].name)
        if Qt_Orientation == QtCore.Qt.Vertical and int_role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(str(self.features[0].index.values[p_int]))
        return QtCore.QVariant()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled

    def get_data(self):
        return self.data_table
