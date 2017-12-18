import pandas as pd
from PyQt5 import QtCore

from tables.models.pandas import PandasTableModel


class NormTableModel(PandasTableModel):
    def __init__(self, data, normalization, nominal_denominator=None, labels=None):
        super(NormTableModel, self).__init__(data=data)
        self.norm = normalization
        self.norm_data = self.norm.apply(self.data_table)
        if labels is None:
            self.cluster_column = pd.Series('?', index=self.norm_data.index, name='Cluster#')
        else:
            self.cluster_column = pd.Series(labels, index=self.norm_data.index, name='Cluster#')
        if nominal_denominator is None:
            self.nominal_denominator = dict()
        else:
            self.nominal_denominator = nominal_denominator

    def get_actual_data(self):
        nd = self.norm_data.copy()
        nd['Cluster#'] = self.cluster_column
        return nd

    def update(self, data_in):
        self.data_table = data_in
        self.norm_data = self.norm.apply(self.data_table, self.nominal_denominator)

    def set_cluster(self, labels):
        self.layoutAboutToBeChanged.emit()
        self.cluster_column = pd.Series(labels, name=self.cluster_column.name)
        self.layoutChanged.emit()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            i = index.row()
            j = index.column()
            if j == super().columnCount():
                return '{0}'.format(self.cluster_column.iat[i])
            return '{0}'.format(self.norm_data.iat[i, j])
        else:
            return QtCore.QVariant()

    def headerData(self, col, orientation, role=None):
        if col == super().columnCount() and orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            new_name = self.cluster_column.name
            for marker in self.markers.keys():
                if self.markers[marker] == col:
                    new_name += " (" + marker + ")"
            return new_name
        return super().headerData(col, orientation, role)

    def set_norm(self, normalization):
        self.norm = normalization
        self.update(self.data_table)

    def get_norm(self):
        return self.norm

    def get_data(self):
        return self.norm_data

    def columnCount(self, parent=QtCore.QModelIndex(), *args, **kwargs):
        super_count = super().columnCount(parent=QtCore.QModelIndex())
        if super_count != 0:
            return super_count + 1
        else:
            return super_count
