from tables.models.norm import NormTableModel
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

    def set_data(self, value):
        self._data = value
        model = NormTableModel(self._data, self._norm, )
        self._table_view.setModel(model)

    def update_norm(self):
        settings = QSettings('ECT', 'hse')
        enabled = settings.value('NormEnabled', type=bool)
        center = settings.value('Center', type=str)
        range_ = settings.value('Range', type=str)
        self._norm = Normalization(enabled, center, range_)
        self.set_data(self.data)

    @property
    def norm(self):
        return self._norm

    def add_column(self, series):
        try:
            pd.to_numeric(series)
            data = self.data
            data[series.name] = series
            self.set_data(data)
        except ValueError:
            msg = QMessageBox()
            msg.setFixedSize(400, 500)
            msg.setIcon(QMessageBox.Information)
            msg.setText("Nominal feature.\n")
            msg.setText(
                "The selected feature \"{}\" is nominal.\nWould you like one-hot encode it?".format(series.name))
            msg.setWindowTitle("Nominal feature")
            msg.setDetailedText("Nominal features can't be processed directly. "
                                "One need to encode it by some numeric values."
                                "One way to do it is one-hot encoding.")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            res = msg.exec_()
            if res == QMessageBox.Ok:
                self.do_one_hot(series)

    def do_one_hot(self, series):
        df = self.data
        if len(self.data) == 0:
            df = pd.DataFrame()
        unique_values = series.unique()
        for uv in unique_values:
            new_col = pd.Series(data=0, index=series.index)
            new_col[series == uv] = 1
            df[series.name + str('[' + uv + ']')] = new_col
            if len(unique_values) == 2:
                break
        self.set_data(df)

    def add_context_actions(self, menu, column):
        try:
            self.data.iloc[:, column]
        except IndexError:
            for action in menu.actions():
                if action.text() == "Delete":
                    action.setDisabled(True)
