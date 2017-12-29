from tables.table import Table
from normalization import Normalization
from PyQt5.QtCore import *
from tables.models.norm_model import NormTableModel


class NormTable(Table):
    def __init__(self, table_view, parent):
        super().__init__(table_view, parent)
        self._norm = None
        self.update_norm()
        self.nominal_denominator = dict()
        self.cluster_feature = None

    def get_model(self):
        try:
            return NormTableModel(self._features, self._norm, cluster_feature=self.cluster_feature)
        except AttributeError:
            return NormTableModel(self._features, self._norm)

    def update_norm(self):
        settings = QSettings('ECT', 'hse')
        enabled = settings.value('NormEnabled', type=bool)
        center = settings.value('Center', type=str)
        range_ = settings.value('Range', type=str)
        self._norm = Normalization(enabled, center, range_)
        self.parent.status_bar.status()
        self.set_features(self.features)

    def _get_feature_by_column(self, column):
        try:
            return self._features[column]
        except:
            return self._table_view.model().cluster_feature

    @property
    def norm(self):
        return self._norm

    def add_columns(self, features):
        self.set_features(self._features + features)
        self.cluster_feature = self._table_view.model().cluster_feature

    def add_context_actions(self, menu, column):
        try:
            self.features[column]
        except IndexError:
            for action in menu.actions():
                if action.text() == "Delete":
                    action.setDisabled(True)
