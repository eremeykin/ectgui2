from tables.table import Table
from normalization import Normalization
from tables.models.features_model import FeaturesTableModel
from settings import Settings


class NormTable(Table):
    def __init__(self, table_view, parent):
        super().__init__(table_view, parent, hide_scroll=True)
        self._norm = None
        self.update_norm()
        self.nominal_denominator = dict()
        self._norm_features = [self._norm.apply(f) for f in self._features]

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
        self._norm_features = [self._norm.apply(f) for f in self._features]
        self.parent.status_bar.status()
        # model = FeaturesTableModel(features=self.features)
        # self._table_view.setModel(model)
        # self.set_features(self._features) # update (do not remove)

    @property
    def norm(self):
        return self._norm

    @property
    def features(self):
        return self._norm_features

    def set_features(self, features):
        if not self._check_name_uniquness(features):
            return
        self._features = features
        self.update_norm()
        model = FeaturesTableModel(features=self.features)
        self._table_view.setModel(model)

    def context_menu(self, point, feature=None):
        menu = super().context_menu(point)
        menu.popup(self._table_view.horizontalHeader().mapToGlobal(point))

    def update(self):
        for _f,f in zip(self._features, self.features):
            _f._markers=f._markers # TODO reorganize
        self.set_features(self._features)

