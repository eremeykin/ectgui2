from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import pandas as pd
from hist_dialog.hist_dialog import HistDialog
from tables.models.features_model import FeaturesTableModel
from feature import Feature

class Table:

    def __init__(self, table_view, parent, hide_scroll=False):
        self.parent = parent
        self._table_view = table_view
        if hide_scroll:
            table_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._features = []
        # set context menu
        header = self._table_view.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(lambda p: self.context_menu(point=p))

    def connect(self, other_table):
        sb1 = self._table_view.verticalScrollBar()
        sb2 = other_table._table_view.verticalScrollBar()
        sb1.valueChanged.connect(sb2.setValue)
        sb2.valueChanged.connect(sb1.setValue)

    @property
    def features(self):
        return self._features

    def add_columns(self, features):
        self.set_features(self._features + features)

    def context_menu(self, point, feature=None): # feature parameter is only for testing
        column = self._table_view.horizontalHeader().logicalIndexAt(point.x())
        feature = self.features[column] if feature is None else feature
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
        for marker in Feature.markers_dct.keys():
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
        # menu.popup(self._table_view.horizontalHeader().mapToGlobal(point))
        return menu

    def action_set_as(self, feature, marker):
        feature.add_markers(marker)
        # self.set_features(self._features)
        self.parent.update()  # important! if we set X for example on diag(norm), while X is already on diag(raw) we
        # must update all

    def action_set_as_index(self, feature):
        self.delete_features([feature])
        model = FeaturesTableModel(features=self._features, index=feature.series.tolist())
        self._table_view.setModel(model)

    def add_context_actions(self, menu, column):
        pass

    def _check_name_uniquness(self, features):
        for i in range(len(features)):
            for j in range(i + 1, len(features)):
                if features[i] == features[j]:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Can't complete operation.\nThe uniqueness of the feature names is violated")
                    msg.exec_()
                    return False
        return True

    def set_features(self, features):
        if not self._check_name_uniquness(features):
            return
        self._features = features
        model = FeaturesTableModel(features=self.features)
        self._table_view.setModel(model)

    def delete_features(self, features):
        remaining = []
        for feature in self._features:
            if feature not in features:
                remaining.append(feature)
        self.set_features(remaining)

    def translate(self, text):
        return text

    def update(self):
        self.set_features(self.features)
