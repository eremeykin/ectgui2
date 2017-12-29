from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import pandas as pd
from hist_dialog.hist_dialog import HistDialog
from tables.models.features_model import FeaturesTableModel

class Table:
    markers = ["X", "Y", "C"]

    def __init__(self, table_view, parent):
        self.parent = parent
        self._table_view = table_view
        self._features = []
        # set context menu
        header = self._table_view.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(lambda p: self.context_menu(point=p))

    @property
    def features(self):
        return self._features

    def _get_feature_by_column(self, column):
        return self.features[column]

    def context_menu(self, point):
        column = self._table_view.horizontalHeader().logicalIndexAt(point.x())
        feature = self._get_feature_by_column(column)
        # feature = self.features[column]
        menu = QMenu(self.parent)
        action_delete = QAction(self.parent)
        action_delete.triggered.connect(lambda x: self.delete_features([feature]))
        action_delete.setObjectName("DeleteAction")
        action_delete.setText(self.translate("Delete"))

        action_hist = QAction(self.parent)
        action_hist.triggered.connect(lambda x: HistDialog.ask(self.parent, feature))
        action_hist.setObjectName("HistAction")
        action_hist.setText(self.translate("Histogram"))

        set_actions = []
        for marker in self.markers:
            action_set_as = QAction(self.parent)
            action_set_as.setObjectName("actionSetAs" + marker)

            def fnct(fake=False, m=marker):
                return self.action_set_as(feature, m)

            action_set_as.triggered.connect(fnct)
            action_set_as.setText(self.translate("as " + marker))
            set_actions.append(action_set_as)

        if len(set_actions) > 0:
            menu_set = QMenu(menu)
            menu_set.setTitle("Set")
            for action in set_actions:
                menu_set.addAction(action)
            menu.addMenu(menu_set)

        menu.addAction(action_hist)
        menu.addAction(action_delete)
        self.add_context_actions(menu, column)
        menu.popup(self._table_view.horizontalHeader().mapToGlobal(point))
        return menu

    def action_set_as(self, feature, marker):
        for f in self.parent.all_features():
            f.remove_markers(set([marker]))
        self.parent.update()
        feature.add_markers(marker)
        self.set_features(self._features)
        self.parent.update()

    def add_context_actions(self, menu, column):
        pass

    def get_model(self):
        return FeaturesTableModel(features=self._features)

    def set_features(self, features):
        for i in range(len(features)):
            for j in range(i + 1, len(features)):
                if features[i] == features[j]:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Can't complete operation.\nThe uniqueness of the feature names is violated")
                    msg.exec_()
                    return
        self._features = features
        model = self.get_model()
        self._table_view.setModel(model)

    def delete_features(self, features):
        remaining = []
        for feature in self._features:
            if feature not in features:
                remaining.append(feature)
        self.set_features(remaining)

    def translate(self, text):
        return text
