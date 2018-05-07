from tables.table import Table
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class RawTable(Table):
    def __init__(self, table_view, parent):
        super().__init__(table_view, parent, hide_scroll=False)

    def context_menu(self, point):
        column = self._table_view.horizontalHeader().logicalIndexAt(point.x())
        # normalize
        action_normalize = QAction(self.parent)
        action_normalize.triggered.connect(lambda x: self.parent.normalize_features([self._features[column]], ask_nominal=True))
        action_normalize.setText(self.translate("Normalize"))
        # to labels
        action_to_labels = QAction(self.parent)
        action_to_labels.triggered.connect(lambda x: self.parent.to_labels(self._features[column]))
        action_to_labels.setText(self.translate("To labels"))
        menu = super().context_menu(point)
        menu.addAction(action_normalize)
        menu.addAction(action_to_labels)
        menu.popup(self._table_view.horizontalHeader().mapToGlobal(point))
        return menu
