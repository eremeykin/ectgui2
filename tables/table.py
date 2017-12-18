from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import pandas as pd

class Table:
    def __init__(self, table_view, parent):
        self.parent = parent
        self._table_view = table_view
        self._data = pd.DataFrame()
        # set context menu
        header = self._table_view.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(lambda p: self.context_menu(point=p))

    @property
    def data(self):
        return self._data

    def context_menu(self, point):
        column = self._table_view.horizontalHeader().logicalIndexAt(point.x())
        menu = QMenu(self.parent)
        action_delete = QAction(self.parent)
        action_delete.triggered.connect(lambda x: self.action_delete_column(column))
        action_delete.setObjectName("DeleteAction")
        action_delete.setText(self.translate("Delete"))
        menu.addAction(action_delete)
        self.add_context_actions(menu, column)
        menu.popup(self._table_view.horizontalHeader().mapToGlobal(point))
        return menu

    def add_context_actions(self, menu, column):
        pass

    def set_data(self, data):
        raise NotImplemented

    def action_delete_column(self, column):
        df = self._data
        df.drop(df.columns[[column]], axis=1, inplace=True)
        self.set_data(df)

    def translate(self, text):
        return text
