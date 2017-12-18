from tables.table import Table
from tables.models.raw import RawTableModel
from PyQt5.QtWidgets import *


class RawTable(Table):
    def __init__(self, table_view, parent):
        super().__init__(table_view, parent)

    def set_data(self, value):
        self._data = value
        model = RawTableModel(value)
        self._table_view.setModel(model)

    def add_context_actions(self, menu, column):
        action_delete = QAction(self.parent)
        action_delete.triggered.connect(lambda x: self.parent.normalize_column(self.data.iloc[:, column]))
        action_delete.setText(self.translate("Normalize"))
        menu.addAction(action_delete)
