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

    def set_features(self, features):
        if not self._check_name_uniquness(features):
            return
        self._features = features
        cf = []
        model = FeaturesTableModel(features=[self._norm.apply(f) for f in self._features] + cf)
        self._table_view.setModel(model)

    def context_menu(self, point, feature=None):
        menu = super().context_menu(point)
        menu.popup(self._table_view.horizontalHeader().mapToGlobal(point))
