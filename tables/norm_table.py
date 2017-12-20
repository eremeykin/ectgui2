from tables.models.norm_model import NormTableModel
from tables.table import Table
import pandas as pd
from normalization import Normalization
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class NormTable(Table):
    def __init__(self, table_view, parent):
        super().__init__(table_view, parent)
        self._norm = None
        self.update_norm()
        self.nominal_denominator = dict()

    def get_model(self):
        return NormTableModel(self._features, self._norm)

    def update_norm(self):
        settings = QSettings('ECT', 'hse')
        enabled = settings.value('NormEnabled', type=bool)
        center = settings.value('Center', type=str)
        range_ = settings.value('Range', type=str)
        self._norm = Normalization(enabled, center, range_)
        self.parent.status_bar.status()
        self.set_features(self.features)

    @property
    def norm(self):
        return self._norm

    def add_columns(self, features):
        self.set_features(self._features + features)

    def add_context_actions(self, menu, column):
        try:
            self.features[column]
        except IndexError:
            for action in menu.actions():
                if action.text() == "Delete":
                    action.setDisabled(True)
