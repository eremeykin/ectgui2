import os

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

ui_file = os.path.join(os.path.dirname(__file__), '../ui/select_features.ui')
UI_SelectFeatures, QtBaseClass = uic.loadUiType(ui_file)


class SelectFeaturesDialog(UI_SelectFeatures, QDialog):
    def __init__(self, parent):
        super(SelectFeaturesDialog, self).__init__(parent)
        self.setupUi(self)
        for feature in parent.raw_table.features:
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
    def ask(cls, parent):
        dialog = cls(parent)
        if dialog.exec_() == QDialog.Accepted:
            return None
        raise BaseException("Rejected")
