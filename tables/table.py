from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import pandas as pd


class Table:
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

    def context_menu(self, point):
        column = self._table_view.horizontalHeader().logicalIndexAt(point.x())
        feature = self._features[column]
        menu = QMenu(self.parent)
        action_delete = QAction(self.parent)
        action_delete.triggered.connect(lambda x: self.delete_features([feature]))
        action_delete.setObjectName("DeleteAction")
        action_delete.setText(self.translate("Delete"))
        menu.addAction(action_delete)
        self.add_context_actions(menu, column)
        menu.popup(self._table_view.horizontalHeader().mapToGlobal(point))
        return menu

    def add_context_actions(self, menu, column):
        pass

    def get_model(self):
        raise NotImplemented

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
