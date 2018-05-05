import os

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

ui_file = os.path.join(os.path.dirname(__file__), '../ui/select_features_all.ui')
UI_SelectFeatures, QtBaseClass = uic.loadUiType(ui_file)


class SelectFeaturesAllDialog(UI_SelectFeatures, QDialog):
    def __init__(self, parent, features_raw, features_norm, features_labels):
        super(SelectFeaturesAllDialog, self).__init__(parent)
        self.setupUi(self)
        self.features_raw = features_raw
        self.features_norm = features_norm
        self.features_labels = features_labels
        for features_list, qlist in zip([self.features_raw, self.features_norm, self.features_labels],
                                        [self.list_widget_raw, self.list_widget_norm, self.list_widget_labels]):
            if len(features_list) < 1:
                self.group(qlist).hide()
                continue
            for feature in features_list:
                item = QListWidgetItem("{}".format(feature.name))
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked if feature.is_nominal else Qt.Checked)
                qlist.addItem(item)
            none, inverse, all = self.buttons(qlist)

            none.clicked.connect(lambda x, ql=qlist: self.check_none(ql))
            inverse.clicked.connect(lambda x, ql=qlist: self.check_inverse(ql))
            all.clicked.connect(lambda x, ql=qlist: self.check_all(ql))

    def group(self, qlist):
        if qlist == self.list_widget_raw:
            return self.group_box_raw
        if qlist == self.list_widget_norm:
            return self.group_box_norm
        if qlist == self.list_widget_labels:
            return self.group_box_labels

    def buttons(self, qlist):
        if qlist == self.list_widget_raw:
            return self.push_button_raw_none, self.push_button_raw_inverse, self.push_button_raw_all
        if qlist == self.list_widget_norm:
            return self.push_button_norm_none, self.push_button_norm_inverse, self.push_button_norm_all
        if qlist == self.list_widget_labels:
            return self.push_button_labels_none, self.push_button_labels_inverse, self.push_button_labels_all

    def check_all(self, qlist):
        for index in range(qlist.count()):
            item = qlist.item(index)
            item.setCheckState(Qt.Checked)

    def check_none(self, qlist):
        print(qlist)
        for index in range(qlist.count()):
            item = qlist.item(index)
            item.setCheckState(Qt.Unchecked)

    def check_inverse(self, qlist):
        for index in range(qlist.count()):
            item = qlist.item(index)
            if item.checkState() == Qt.Unchecked:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def _checked(self, qlist, features):
        items = [qlist.item(i) for i in range(qlist.count())]
        res_features = []
        for feature, item in zip(features, items):
            if item.checkState() == Qt.Checked:
                res_features.append(feature)
        return res_features

    def checked_raw(self):
        return self._checked(self.list_widget_raw, self.features_raw)

    def checked_norm(self):
        return self._checked(self.list_widget_norm, self.features_norm)

    def checked_labels(self):
        return self._checked(self.list_widget_labels, self.features_labels)

    @classmethod
    def ask(cls, parent, features_raw=[], features_norm=[], features_labels=[]):
        if not features_raw and not features_norm and not features_labels:
            msg = QMessageBox()
            msg.setWindowTitle("No features")
            msg.setText("There is no features")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            return QDialog.Rejected
        dialog = cls(parent, features_raw, features_norm, features_labels)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.checked_raw(), dialog.checked_norm(), dialog.checked_labels()
        return QDialog.Rejected
