import pandas as pd
from PyQt5 import QtCore
from tables.models.features_model import FeaturesTableModel
from tables.models.pandas import PandasTableModel
from feature import Feature


class NormTableModel(FeaturesTableModel):
    def __init__(self, features, normalization, labels=None):
        super(NormTableModel, self).__init__(features=features)
        self.norm = normalization
        self.normed_features = [self.norm.apply(f) for f in features]
        if len(self.features) == 0:
            self.cluster_feature = None
        else:
            index = self.features[0].series.index
            if labels is None:
                s = pd.Series('?', index=index, name='Cluster#')
            else:
                s = pd.Series(labels, index=index, name='Cluster#')
            self.cluster_feature = Feature(s)

    def set_cluster(self, labels):
        self.layoutAboutToBeChanged.emit()
        s = pd.Series(labels, name=self.cluster_feature.name)
        self.cluster_feature = Feature(s)
        self.layoutChanged.emit()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            i = index.row()
            j = index.column()
            if j == super().columnCount():
                return '{0}'.format(self.cluster_feature[i])
            return '{0}'.format(self.normed_features[j][i])
        else:
            return QtCore.QVariant()

    def get_data(self):
        return self.norm_data

    def headerData(self, col, orientation, role):
        if col == super().columnCount() and orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.cluster_feature.name
        return super().headerData(col, orientation, role)

    def columnCount(self, parent=QtCore.QModelIndex(), *args, **kwargs):
        super_count = super().columnCount(parent=QtCore.QModelIndex())
        if super_count != 0:
            return super_count + 1
        else:
            return super_count
