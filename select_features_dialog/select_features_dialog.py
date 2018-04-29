import os

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

ui_file = os.path.join(os.path.dirname(__file__), '../ui/select_features.ui')
UI_SelectFeatures, QtBaseClass = uic.loadUiType(ui_file)


class SelectFeaturesDialog(UI_SelectFeatures, QDialog):
    def __init__(self, parent, features):
        super(SelectFeaturesDialog, self).__init__(parent)
        self.setupUi(self)
        self.features = features
        for feature in self.features:
            item = QListWidgetItem("{}".format(feature.name))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked if feature.is_nominal else Qt.Checked)
            self.list_widget.addItem(item)
        self.push_button_all.clicked.connect(self.check_all)
        self.push_button_none.clicked.connect(self.check_none)
        self.push_button_inverse.clicked.connect(self.check_inverse)

    def check_all(self):
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            item.setCheckState(Qt.Checked)

    def check_none(self):
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            item.setCheckState(Qt.Unchecked)

    def check_inverse(self):
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.checkState() == Qt.Unchecked:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    @classmethod
    def ask(cls, parent, features):
        if len(features)<1:
            msg = QMessageBox()
            msg.setWindowTitle("No features")
            msg.setText("There is no features")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            return QDialog.Rejected
        dialog = cls(parent, features)
        if dialog.exec_() == QDialog.Accepted:
            items = [dialog.list_widget.item(i) for i in range(dialog.list_widget.count())]
            res_features = []
            for feature, item in zip(features, items):
                if item.checkState() == Qt.Checked:
                    res_features.append(feature)
            return res_features
        return QDialog.Rejected
