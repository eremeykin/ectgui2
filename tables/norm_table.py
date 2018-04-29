from tables.table import Table
from normalization import Normalization
from PyQt5.QtCore import *
import pandas as pd
from feature import Feature
from tables.models.features_model import FeaturesTableModel
from settings import Settings

class NormTable(Table):
    def __init__(self, table_view, parent):
        super().__init__(table_view, parent)
        self._norm = None
        self.update_norm()
        self.nominal_denominator = dict()
        self.cluster_feature = None

    def update_norm(self):
        settings = Settings()
        enabled = settings.norm_enabled
        center = settings.center
        if not center:
            center = "None"
        spread = settings.spread
        if not spread:
            spread = "Unity"
        power = settings.power
        if not power:
            power = 2
        self._norm = Normalization(enabled, center, spread, power)
        self.parent.status_bar.status()
        self.set_features(self.features)

    @property
    def norm(self):
        return self._norm

    def set_cluster_feature(self, cluster_feature):
        self.cluster_feature = cluster_feature
        self.set_features(self.features)

    def set_features(self, features):
        if not self._check_name_uniquness(features):
            return
        self._features = features
        cf = []
        if len(features) > 0:
            if self.cluster_feature is None:
                data = list("?" * len(features[0]))
                index = features[0].series.index
                name = "cluster"
                series = pd.Series(data=data, index=index, dtype=str, name=name)
                self.cluster_feature = Feature(series=series, name=name, is_norm=True)
            cf.append(self.cluster_feature)
        else:
            self.cluster_feature = None
        model = FeaturesTableModel(features=[self._norm.apply(f) for f in self._features] + cf)
        self._table_view.setModel(model)

    def add_columns(self, features):
        self.set_features(self._features + features)

    def context_menu(self, point, feature=None):
        try:
            column = self._table_view.horizontalHeader().logicalIndexAt(point.x())
            feature = self.features[column]
            menu = super().context_menu(point)
        except IndexError:
            menu = super().context_menu(point, self.cluster_feature)
            for action in menu.actions():
                if action.text() == "Delete":
                    action.setDisabled(True)
        menu.popup(self._table_view.horizontalHeader().mapToGlobal(point))

    @property
    def actual_features(self):
        if len(self.features) > 0:
            return self._table_view.model().get_features()[:-1]  # exclude cluster feature
        return []
