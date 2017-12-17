from PyQt5 import QtGui
from PyQt5.QtGui import QColor

__author__ = 'eremeykin'
import pandas as pd
from PyQt5 import QtCore


class PandasTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data=pd.DataFrame()):
        super(PandasTableModel, self).__init__()
        self.data_table = data
        self.layout = 'Panel'  # TODO Delete?
        self.markers = dict()
        if self.columnCount() == 0:
            self.data_table = pd.DataFrame()

    def get_actual_data(self):
        return self.data_table

    def get_by_marker(self, marker):
        return self.get_actual_data()[self.markers[marker]]

    def set_marker(self, column_name, marker):
        self.markers[marker] = column_name

    def del_all_markers(self):
        self.markers = dict()

    def del_marker(self, marker):
        try:
            del self.markers[marker]
        except KeyError:
            pass

    def update(self, data_in):
        self.data_table = data_in

    def rowCount(self, QModelIndex_parent=QtCore.QModelIndex(), *args, **kwargs):
        return self.data_table.shape[0]

    def columnCount(self, QModelIndex_parent=QtCore.QModelIndex(), *args, **kwargs):
        if len(self.data_table.shape) > 1:
            return self.data_table.shape[1]
        if self.data_table.shape[0] == 0:
            return 1
        return 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        i = index.row()
        j = index.column()
        if role == QtCore.Qt.DisplayRole:
            return '{0}'.format(self.data_table.iat[i, j])
        if role == QtCore.Qt.BackgroundColorRole:
            return self.color_injection(i, j)
        else:
            return QtCore.QVariant()

    def color_injection(self, i, j):
        return QtCore.QVariant()

    def headerData(self, p_int, Qt_Orientation, int_role=None):
        if Qt_Orientation == QtCore.Qt.Horizontal and int_role == QtCore.Qt.DisplayRole:
            c_name = self.data_table.columns.values[p_int]
            new_name = c_name
            for marker in self.markers.keys():
                if self.markers[marker] == p_int:
                    new_name += " (" + marker + ")"
            return QtCore.QVariant(new_name)
        if Qt_Orientation == QtCore.Qt.Vertical and int_role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(str(self.data_table.index.values[p_int]))
        return QtCore.QVariant()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled

    def get_data(self):
        return self.data_table
