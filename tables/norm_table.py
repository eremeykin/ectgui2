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

    def set_features(self, features):
        self._features = features
        model = NormTableModel(self._features, self._norm, )
        self._table_view.setModel(model)

    def update_norm(self):
        settings = QSettings('ECT', 'hse')
        enabled = settings.value('NormEnabled', type=bool)
        center = settings.value('Center', type=str)
        range_ = settings.value('Range', type=str)
        self._norm = Normalization(enabled, center, range_)
        self.set_features(self.features)

    @property
    def norm(self):
        return self._norm

    def _is_ok(self, name):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Nominal feature.\n")
        msg.setText(
            "The selected feature \"{}\" is nominal.\nWould you like one-hot encode it?".format(name))
        msg.setWindowTitle("Nominal feature")
        msg.setDetailedText("Nominal features can't be processed directly. "
                            "One need to encode it by some numeric values."
                            "One way to do it is one-hot encoding.")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return msg.exec_() == QMessageBox.Ok

    def add_column(self, feature):
        if feature.is_nominal:
            if not self._is_ok(feature.name):
                return
            new_features = feature.expose_one_hot()
        else:
            new_features = [feature]
        new_features = self._features + new_features
        self.set_features(new_features)

    def add_context_actions(self, menu, column):
        try:
            self.features[column]
        except IndexError:
            for action in menu.actions():
                if action.text() == "Delete":
                    action.setDisabled(True)
