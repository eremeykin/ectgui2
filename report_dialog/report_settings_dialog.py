import os
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from plot.plot import plot_svd
import matplotlib.pyplot as plt
from PyQt5 import QtGui
from PyQt5.QtGui import *
from report.report_html_printer import ReportHTMLPrinter
from report.report_plain_printer import ReportPlainPrinter
from select_features_dialog.select_features_dialog_all import SelectFeaturesAllDialog
from settings import Settings

ui_file = os.path.join(os.path.dirname(__file__), '../ui/report_settings.ui')
UI_ReportSettingsDialog, QtBaseClass = uic.loadUiType(ui_file)


class ReportSettingsDialog(UI_ReportSettingsDialog, QDialog):
    def __init__(self, parent, labels_features=[], clusters=[]):
        super(ReportSettingsDialog, self).__init__(parent)
        self.setupUi(self)
        settings = Settings()
        self.font_spin.setValue(settings.report_settings_font)
        self.check_box.setChecked(settings.report_settings_calc_sw)
        self.threshold_spin.setValue(settings.report_settings_threshold)
        for feature in labels_features:
            item = QListWidgetItem("{}".format(feature.name))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.conv_list.addItem(item)
        for feature in labels_features:
            item = QListWidgetItem("{}".format(feature.name))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.ari_list.addItem(item)
        for cluster in clusters:
            item = QListWidgetItem("Cluster #{}".format(cluster))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.clusters_list.addItem(item)

    def _checked(self, qlist, features):
        items = [qlist.item(i) for i in range(qlist.count())]
        res_features = []
        for feature, item in zip(features, items):
            if item.checkState() == Qt.Checked:
                res_features.append(feature)
        return res_features

    @classmethod
    def ask(cls, parent, all_raw_features=[], labels_features=[], clusters=[]):
        dialog = cls(parent, labels_features, clusters)
        if dialog.exec_() == QDialog.Accepted:
            font_size, calculate_sw, threshold = dialog.font_spin.value(), dialog.check_box.isChecked(), dialog.threshold_spin.value()
            ari_features = dialog._checked(dialog.ari_list, labels_features)
            conv_features = dialog._checked(dialog.conv_list, labels_features)
            clusters = dialog._checked(dialog.clusters_list, clusters)
            settings = Settings()
            settings.report_settings_font = font_size
            settings.report_settings_calc_sw = calculate_sw
            settings.report_settings_threshold = threshold
            clusters_index = None
            if len(clusters) > 0:
                answer = SelectFeaturesAllDialog.ask(parent, features_raw=all_raw_features,
                                                     policy=[SelectFeaturesAllDialog.ONE_RAW])
                if answer != QDialog.Rejected:
                    features_raw, features_norm, features_labels = answer
                    clusters_index = features_raw[0]
            return font_size, calculate_sw, threshold, ari_features, conv_features, clusters, clusters_index
        return QDialog.Rejected
