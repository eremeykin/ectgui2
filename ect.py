import os
import sys

import pandas as pd
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from norm_settings_dialog.norm_settings_dialog import NormSettingDialog
from feature import Feature
import numpy as np
from status_bar.status_bar import StatusBar
from tables.raw_table import RawTable
from tables.norm_table import NormTable
from select_features_dialog.select_features_dialog import SelectFeaturesDialog
from generator_dialog.generator_dialog import GeneratorDialog
from save_labels_dialog.save_labels_dialog import SaveLabelsDialog
from itertools import cycle
import matplotlib.pyplot as plt
from plot.plot import plot_svd
from parameters_dialog.a_ward_dialog import AWardParamsDialog
from parameters_dialog.a_ward_dialog_pb import AWardPBParamsDialog
from parameters_dialog.bikm_r_dialog import BiKMeansRParamsDialog
from parameters_dialog.auto_choose_p import AutoChoosePDialog
from report_dialog.text_report import TextReportDialog
from report import Report
from time import time
import itertools

ui_file = os.path.join(os.path.dirname(__file__), 'ui/main.ui')
ui_file_norm_settings = os.path.join(os.path.dirname(__file__), 'ui/norm_settings.ui')

UI_ECT, QtBaseClass = uic.loadUiType(ui_file)


class ECT(UI_ECT, QMainWindow):
    parse_triggered = pyqtSignal()

    load_last = True

    class LoadDataThread(QThread):

        def __init__(self, data_file):
            super().__init__()
            self.data_file = data_file
            self.data = None

        def run(self):
            self.data = pd.read_csv(self.data_file)

    def __init__(self, parent=None):
        super(ECT, self).__init__(parent)
        self.setupUi(self)
        # load settings
        self.qt_settings = QSettings('ECT', 'hse')
        # bind actions
        self.action_open.triggered.connect(self.open)
        self.action_exit.triggered.connect(sys.exit)
        self.action_settings.triggered.connect(self.settings)
        self.action_normalize.setChecked(self.qt_settings.value("NormEnabled", type=bool))
        self.action_normalize.triggered.connect(self.normalize)
        self.action_normalize_all.triggered.connect(self.normalize_all_features)
        self.action_clear_normalized.triggered.connect(self.clear_normalized)
        self.action_generate.triggered.connect(self.generate)
        self.action_by_markers.triggered.connect(self.plot_by_markers)
        self.action_svd_raw.triggered.connect(lambda: self.svd(self.raw_table))
        self.action_svd_normalized.triggered.connect(lambda: self.svd(self.norm_table))
        self.action_remove_markers.triggered.connect(self.remove_markers)
        self.action_a_ward.triggered.connect(self.a_ward)
        self.action_a_ward_pb.triggered.connect(self.a_ward_pb)
        self.action_bikm_r.triggered.connect(self.bikm_r)
        self.action_depddp.triggered.connect(self.depddp)
        self.action_text_report.triggered.connect(self.text_report)
        self.action_table_report.triggered.connect(self.table_report)
        self.status_bar = StatusBar(self)
        self.report = None
        self.raw_table = RawTable(self.table_view_raw, self)
        self.norm_table = NormTable(self.table_view_norm, self)
        self.load_thread = None
        self.status_bar.status("Ready")
        if self.qt_settings.value("LastLoadedFile", type=str) and ECT.load_last:
            self.open(self.qt_settings.value("LastLoadedFile", type=str))

    def _mbox(self, title, text, type=None, details=None, buttons=None):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        if type == "error":
            msg.setIcon(QMessageBox.Critical)
        else:
            msg.setIcon(QMessageBox.Information)
        if details is not None:
            msg.setDetailedText(details)
        if buttons is not None:
            from functools import reduce
            msg.setStandardButtons(reduce(lambda x, y: x | y, buttons))
        return msg.exec_() == QMessageBox.Ok

    def open(self, file_name=None):
        file_name = file_name if file_name else QFileDialog.getOpenFileName(self, 'Open file', '\home')[0]
        if not file_name:
            return
        self.load_thread = ECT.LoadDataThread(file_name)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.status_bar.status("Loading data: {} ...".format(file_name))
        self.load_thread.finished.connect(
            lambda: self.raw_table.set_features(Feature.from_data_frame(self.load_thread.data)))
        self.load_thread.finished.connect(lambda: self.status_bar.status("Ready"))
        self.load_thread.finished.connect(lambda: QApplication.restoreOverrideCursor())
        self.load_thread.finished.connect(lambda: self.qt_settings.setValue("LastLoadedFile", file_name))
        self.load_thread.start()

    def settings(self):
        enabled, center, spread, power = NormSettingDialog.ask(self)
        self.qt_settings.setValue("NormEnabled", enabled)
        self.qt_settings.setValue('Center', center)
        self.qt_settings.setValue('Spread', spread)
        self.qt_settings.setValue('Power', power)
        self.action_normalize.setChecked(enabled)
        self.norm_table.update_norm()

    def remove_markers(self):
        features = self.all_features()
        for f in features:
            f.remove_markers(None, all=True)
        self.update()

    def svd(self, table):
        if not table.features:
            return self._mbox("No features", "There are no features to plot")
        features = SelectFeaturesDialog.ask(self, table.actual_features)
        ax = plt.gca()
        c = None
        for f in self.all_features():
            if 'C' in f.markers:
                c = f.series
        data = np.array([f.series for f in features]).T
        plot_svd(ax, data, labels=c, title="SVD plot", normalize=False)
        plt.show()

    def normalize(self):
        self.qt_settings.setValue("NormEnabled", self.action_normalize.isChecked())
        self.norm_table.update_norm()

    def clear_normalized(self):
        features = SelectFeaturesDialog.ask(self, self.norm_table.actual_features)
        self.norm_table.delete_features(features)

    def normalize_all_features(self):
        features = SelectFeaturesDialog.ask(self, self.raw_table.actual_features)
        self.normalize_features(features, ask_nominal=False)

    def _is_nominal_ok(self, name):
        return self._mbox("Nominal feature.",
                          "The selected feature \"{}\" is nominal.\nWould you like one-hot encode it?".format(name),
                          details="Nominal features can't be processed directly. "
                                  "One need to encode it by some numeric values."
                                  "One way to do it is one-hot encoding.",
                          buttons=[QMessageBox.Ok, QMessageBox.Cancel])

    def generate(self):
        data, labels = GeneratorDialog.ask(self)
        self.save(data, labels)

    def save(self, data, labels=None, file_name=None):
        file_name = file_name if file_name else QFileDialog.getSaveFileName(self, 'Open file', 'dataset.pts')[0]
        if not file_name:
            return
        np.savetxt(file_name, data, delimiter=',', comments='',
                   header=','.join(['F' + str(i) for i in range(data.shape[1])]))
        if labels is not None:
            answer, labels_file = SaveLabelsDialog.ask(self)
            if answer == "Yes":
                data = np.hstack((data, labels[:, None]))
                np.savetxt(file_name, data, delimiter=',', comments='',
                           header=','.join(['F' + str(i) for i in range(data.shape[1])]))
            if answer == "Separately":
                np.savetxt(labels_file, labels, delimiter=',', comments='', header="L")
            if answer == "No":
                return

    def plot_by_markers(self):
        colors = cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k', ])
        markers = cycle(['o', 'p', '.', 's', '8', 'h'])
        size = cycle([75, 150, 125, 100])
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.axis('equal')
        features = self.all_features()
        c, x, y = None, None, None
        for f in features:
            if 'C' in f.markers:
                c = f.series
            if 'X' in f.markers:
                x = f.series
            if 'Y' in f.markers:
                y = f.series
        if x is None or y is None:
            return self._mbox("Marker is not set", "One (or both) of markers: X,Y is not set. Can't plot.")
        if c is not None:
            for l in np.unique(c):
                s = next(size)
                m = next(markers)
                clr = next(colors)
                plt.scatter(x[c == l], y[c == l], s=s, marker=m, color=clr)
        else:
            plt.scatter(x, y, s=150, marker='o', color='b')
        plt.grid(True)
        plt.show()

    def all_features(self, include_cluster_feature=True):
        features = []
        features.extend(self.raw_table.features)
        features.extend(self.norm_table.features)
        if include_cluster_feature and self.norm_table.cluster_feature is not None:
            features.extend([self.norm_table.cluster_feature])
        return features

    def update(self):
        self.raw_table.set_features(self.raw_table.features)
        self.norm_table.set_features(self.norm_table.features)

    def normalize_features(self, features, ask_nominal=False):
        features_to_norm = []
        for feature in features:
            if feature.is_nominal:
                if ask_nominal:
                    if self._is_nominal_ok(feature.name):
                        features_to_norm.extend(feature.expose_one_hot(norm=True))
                    else:
                        continue
                else:
                    features_to_norm.extend(feature.expose_one_hot(norm=True))
            else:
                features_to_norm.append(Feature.copy(feature, is_norm=True))
        self.norm_table.add_columns(features_to_norm)

    def get_data(self):
        actual_features = self.norm_table.actual_features
        if len(actual_features) < 1:
            self._mbox("No features", "There are no normalized features.\nCan't run clustering.")
            return None
        return np.array([f.series for f in actual_features]).T

    def auto_choose_p(self, parent):
        start, step, end, clusters_number = AutoChoosePDialog.ask(parent)
        from clustering.agglomerative.utils.choose_p import ChooseP
        arange = np.arange(start, end, step)
        run_choose_p = ChooseP(self.get_data(), clusters_number, arange, arange)
        parent.hide()
        best_p, best_beta, best_cluster_structure, criterion_matrix = run_choose_p()
        pd_table = pd.DataFrame(data=criterion_matrix, index=arange, columns=arange)
        from parameters_dialog.auto_choose_p import AutoChoosePTableDialog
        AutoChoosePTableDialog.ask(self, pd_table)
        result = best_cluster_structure.current_labels()
        self.norm_table.cluster_feature.series = pd.Series(result)
        self.update()

    def a_ward(self):
        from clustering.agglomerative.pattern_initialization.ap_init import APInit
        from clustering.agglomerative.ik_means.ik_means import IKMeans
        from clustering.agglomerative.a_ward import AWard
        self.norm_table.cluster_feature = None
        self.update()
        data = self.get_data()
        if data is None:
            return
        k_star, alpha = AWardParamsDialog.ask(self)
        start = time()
        run_ap_init = APInit(data)
        run_ap_init()
        run_ik_means = IKMeans(run_ap_init.cluster_structure)
        run_ik_means()
        cs = run_ik_means.cluster_structure
        run_a_ward = AWard(cs, k_star, alpha)
        result = run_a_ward()
        end = time()
        self.norm_table.cluster_feature.series = pd.Series(result)
        self.update()
        algorithm = ECT.Algorithm("A-Ward", {"K*": k_star, "merge threshold": alpha})
        self.report = Report(run_a_ward.cluster_structure, algorithm, self.norm_table.norm,
                             self.norm_table.features, end - start)
        self.status_bar.status()

    def a_ward_pb(self):
        from clustering.agglomerative.pattern_initialization.ap_init_pb_matlab import APInitPBMatlabCompatible
        from clustering.agglomerative.utils.matlab_compatible import IMWKMeansClusterStructureMatlabCompatible
        from clustering.agglomerative.ik_means.ik_means import IKMeans
        from clustering.agglomerative.a_ward_pb import AWardPB
        self.norm_table.cluster_feature = None
        self.update()
        data = self.get_data()
        if data is None:
            return
        k_star, p, beta = AWardPBParamsDialog.ask(self)
        start = time()
        run_ap_init_pb = APInitPBMatlabCompatible(data, p, beta)
        run_ap_init_pb()
        # change cluster structure to matlab compatible
        clusters = run_ap_init_pb.cluster_structure.clusters
        new_cluster_structure = IMWKMeansClusterStructureMatlabCompatible(data, p, beta)
        new_cluster_structure.add_all_clusters(clusters)
        run_ik_means = IKMeans(new_cluster_structure)
        run_ik_means()
        cs = run_ik_means.cluster_structure
        run_a_ward_pb = AWardPB(cs, k_star)
        result = run_a_ward_pb()
        end = time()
        self.norm_table.cluster_feature.series = pd.Series(result)
        self.update()
        algorithm = ECT.Algorithm("A-Ward_p_beta", {"K*": k_star, "p": p, "beta": beta})
        self.report = Report(run_a_ward_pb.cluster_structure, algorithm, self.norm_table.norm,
                             self.norm_table.features, end - start)
        self.status_bar.status()

    def bikm_r(self):
        from clustering.divisive.bikm_r import BiKMeansR
        self.norm_table.cluster_feature = None
        self.update()
        data = self.get_data()
        if data is None:
            return
        epsilon = BiKMeansRParamsDialog.ask(self)
        start = time()
        run_bikm_r = BiKMeansR(data, epsilon=epsilon)
        result = run_bikm_r()
        end = time()
        self.norm_table.cluster_feature.series = pd.Series(result)
        self.update()
        algorithm = ECT.Algorithm("Bi K-Means R", {"epsilon": epsilon})
        self.report = Report(run_bikm_r.cluster_structure, algorithm, self.norm_table.norm,
                             self.norm_table.features, end - start)
        self.status_bar.status()

    def depddp(self):
        from clustering.divisive.depddp import DEPDDP
        self.norm_table.cluster_feature = None
        self.update()
        data = self.get_data()
        if data is None:
            return
        start = time()
        run_depddp = DEPDDP(data)
        result = run_depddp()
        end = time()
        self.norm_table.cluster_feature.series = pd.Series(result)
        self.update()
        algorithm = ECT.Algorithm("de PDDP", dict())
        self.report = Report(run_depddp.cluster_structure, algorithm, self.norm_table.norm,
                             self.norm_table.features, end - start)
        self.status_bar.status()

    def text_report(self):
        selected_features = SelectFeaturesDialog.ask(self, self.report.norm_features)
        TextReportDialog.ask(self, self.report, selected_features)

    def table_report(self):
        from report_dialog.table_report import TableDialog
        TableDialog.ask(self, self.report)

    class Algorithm:

        def __init__(self, name, params_dict):
            self.name = name
            self.params = params_dict

        def __str__(self):
            res = "{} with ".format(self.name)
            for key, value in self.params.items():
                if value is None:
                    continue
                res += "{} = {}; ".format(key, value)
            return res


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = ECT()
    widget.show()
    sys.exit(app.exec_())
