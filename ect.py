import logging.config
import sys

logging.config.fileConfig('logging.ini')

from norm_settings_dialog.norm_settings_dialog import NormSettingDialog
from feature import Feature, LabelsFeature
import numpy as np
import pandas as pd
from status_bar.status_bar import StatusBar
from tables.raw_table import RawTable
from tables.norm_table import NormTable
from tables.label_table import LabelTable
from select_features_dialog.select_features_dialog import SelectFeaturesDialog
from select_features_dialog.select_features_dialog_all import SelectFeaturesAllDialog
from generator_dialog.generator_dialog import GeneratorDialog
from save_labels_dialog.save_labels_dialog import SaveLabelsDialog
from itertools import cycle
from report_dialog.text_report import TextReportDialog
from report.report import Report
from algorithms import *
from settings import Settings
from progress_gialog.progress_dialog import ProgressDialog
from result import Result

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
            data = pd.read_csv(self.data_file)
            data.index += 1
            self.data = data

    def __init__(self, parent=None):
        super(ECT, self).__init__(parent)
        self.setupUi(self)
        # load settings
        self.app_settings = Settings()
        # bind actions
        self.action_open.triggered.connect(self.open)
        self.action_exit.triggered.connect(sys.exit)
        self.action_settings.triggered.connect(self.settings)
        self.action_normalize.setChecked(self.app_settings.norm_enabled)
        self.action_normalize.triggered.connect(self.normalize)
        self.action_normalize_all.triggered.connect(self.normalize_all_features)
        self.action_clear.triggered.connect(self.clear)
        self.action_generate.triggered.connect(self.generate)
        self.action_by_markers.triggered.connect(self.plot_by_markers)
        self.action_svd.triggered.connect(lambda: self.svd())
        # self.action_svd_normalized.triggered.connect(lambda: self.svd(self.norm_table))
        self.action_remove_markers.triggered.connect(self.remove_markers)
        # algorithms actions
        self.action_a_ward.triggered.connect(lambda x: self.run_algorithm(AWardAlgorithm))
        self.action_a_ward_pb.triggered.connect(lambda x: self.run_algorithm(AWarbPBAlgorithm))
        self.action_bikm_r.triggered.connect(lambda x: self.run_algorithm(BiKMeansRAlgorithm))
        self.action_depddp.triggered.connect(lambda x: self.run_algorithm(DEPDDPAlgorithm))
        self.action_ik_means.triggered.connect(lambda x: self.run_algorithm(IKMeansAlgorithm))

        self.action_save_data.triggered.connect(lambda: self.save_data(self.norm_table))
        self.action_save_text_report.triggered.connect(lambda: self.save_text_report())
        self.action_labels.triggered.connect(self.show_labels)
        self.show_labels()

        self.action_text_report.triggered.connect(self.text_report)
        self.action_table_report.triggered.connect(self.table_report)
        self.status_bar = StatusBar(self)
        self.result = None
        # tables
        self.raw_table = RawTable(self.table_view_raw, self)
        self.norm_table = NormTable(self.table_view_norm, self)
        self.labels_table = LabelTable(self.table_view_labels, self)

        self.raw_table.connect(self.norm_table)
        self.raw_table.connect(self.labels_table)
        self.load_thread = None
        self.status_bar.status("Ready")
        if self.app_settings.last_loaded_file and ECT.load_last:
            self.open(self.app_settings.last_loaded_file)

    def show_labels(self):
        if self.action_labels.isChecked():
            self.table_view_labels.show()
        else:
            self.table_view_labels.hide()

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

        def load_data():
            data = pd.read_csv(file_name)
            data.index += 1
            self.data = data

        if not os.path.exists(file_name):
            return

        progress = "Load data from file: {}".format(file_name)
        self.status_bar.status(progress)
        p_dialog = ProgressDialog(self, progress, load_data, autofininsh=True)
        p_dialog.run()

        def after():
            self.raw_table.set_features(Feature.from_data_frame(self.data))
            self.app_settings.last_loaded_file = file_name
            self.setWindowTitle("INDACT: {}".format(file_name))
            self.norm_table.delete_features(self.norm_table.features)
            self.status_bar.status("Ready")

        p_dialog.after_finished(after)
        p_dialog.after_cancelled(lambda: self.status_bar.status("Ready"))

    def settings(self):
        dialog_result = NormSettingDialog.ask(self)
        if dialog_result == QDialog.Rejected:
            return
        enabled, center, spread, power = dialog_result
        self.app_settings.norm_enabled = enabled
        self.app_settings.center = center
        self.app_settings.spread = spread
        self.app_settings.power = power
        self.action_normalize.setChecked(enabled)
        self.norm_table.update_norm()

    def save_data(self, table):
        answer = SelectFeaturesAllDialog.ask(self, features_raw=self.raw_table.features,
                                             features_norm=self.norm_table.features,
                                             features_labels=self.labels_table.features)
        if answer == QDialog.Rejected:
            return
        features = []
        for f in answer:
            features.extend(f)
        if len(features) < 1:
            return
        res = QMessageBox.question(self, '', "Would you like add index?", QMessageBox.Yes | QMessageBox.No)
        if res != QMessageBox.Yes and res != QMessageBox.No:
            return
        result = pd.concat([f.series for f in features], axis=1)
        if res == QMessageBox.Yes:
            index = pd.Series(result.index, name="index", dtype=int)
            index.index += 1
            result = pd.concat([index, result], axis=1)
        self.save(result)

    def remove_markers(self):
        Feature.remove_markers([], all=True)
        self.update()

    def svd(self):
        answer = SelectFeaturesAllDialog.ask(self, [], self.norm_table.features)
        if answer == QDialog.Rejected:
            return
        features_raw, features_norm, features_labels = answer
        if answer == QDialog.Rejected or len(features_norm) < 1:
            return
        ax = plt.gca()
        c = None
        if Feature.marked('C'):
            c = Feature.marked('C').series
        data = np.array([f.series for f in features_norm]).T
        plot_svd(ax, data, labels=c, title="SVD plot", normalize=False)
        plt.show()

    def normalize(self):
        self.app_settings.norm_enabled = self.action_normalize.isChecked()
        self.norm_table.update()

    def clear(self):
        policy = [SelectFeaturesAllDialog.ALL_NONE]
        answer = SelectFeaturesAllDialog.ask(self, self.raw_table.features, self.norm_table.features,
                                             self.labels_table.features, policy)
        if answer == QDialog.Rejected:
            return
        features_raw, features_norm, features_labels = answer
        self.raw_table.delete_features(features_raw)
        self.norm_table.delete_features(features_norm)
        self.labels_table.delete_features(features_labels)

    def normalize_all_features(self):
        answer = SelectFeaturesAllDialog.ask(self, self.raw_table.features)
        if answer == QDialog.Rejected:
            return
        features_raw, features_norm, features_labels = answer
        self.normalize_features(features_raw, ask_nominal=False)

    def _is_nominal_ok(self, name):
        return self._mbox("Nominal feature.",
                          "The selected feature \"{}\" is nominal.\nWould you like one-hot encode it?".format(name),
                          details="Nominal features can't be processed directly. "
                                  "One need to encode it by some numeric values."
                                  "One way to do it is one-hot encoding.",
                          buttons=[QMessageBox.Ok, QMessageBox.Cancel])

    def generate(self):
        dialog_result = GeneratorDialog.ask(self)
        if dialog_result == QDialog.Rejected:
            return
        data, labels = dialog_result
        self.save(data, labels)

    def save(self, data, labels=None, file_name=None):
        def sv(some_data, f_name):
            if isinstance(some_data, pd.DataFrame):
                some_data.to_csv(f_name, sep=',', index=False)
            else:
                np.savetxt(f_name, some_data, delimiter=',', comments='',
                           header=','.join(['F' + str(i) for i in range(data.shape[1])]))

        file_name = file_name if file_name else QFileDialog.getSaveFileName(self, 'Open file', 'dataset.pts')[0]
        if not file_name:
            return
        sv(data, file_name)
        if labels is not None:
            res = SaveLabelsDialog.ask(self)
            if res == QDialog.Rejected:
                return
            answer, labels_file = res
            if answer == "Yes":
                data = np.hstack((data, labels[:, None]))
                sv(data, file_name)
            if answer == "Separately":
                sv(labels, labels_file)
            return  # answer No or Rejected

    def plot_by_markers(self):
        colors = cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k', ])
        markers = cycle(['o', 'p', '.', 's', '8', 'h'])
        size = cycle([75, 150, 125, 100])
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # plt.axis('equal')
        c, x, y = None, None, None
        if Feature.marked('C'):
            c = Feature.marked('C').series
        if Feature.marked('X'):
            x = Feature.marked('X').series
        if Feature.marked('Y'):
            y = Feature.marked('Y').series
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

    def update(self):
        self.raw_table.update()
        self.norm_table.update()
        self.labels_table.update()

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
        features = self.norm_table.features
        if len(features) < 1:
            self._mbox("No features", "There are no normalized features.\nCan't run clustering.")
            return None
        return np.array([f.series for f in features]).T

    def run_algorithm(self, algorithm_class):
        self.update()
        data = self.get_data()
        if data is None:
            return
        algorithm = algorithm_class.create(data)
        algorithm.ask_parameters(self)
        if algorithm.parameters is None:
            return

        def _run_alg():
            result_labels, cluster_structure = algorithm()
            return result_labels, cluster_structure

        progress = "Run algorithm: {}".format(algorithm)
        self.status_bar.status(progress)
        p_dialog = ProgressDialog(self, progress, _run_alg, autofininsh=False)
        p_dialog.run()
        p_dialog.after_finished(lambda: self.raw_table.set_features(Feature.from_data_frame(self.data)))

        def set_result():
            series = pd.Series(p_dialog.get_result()[0])  # [0] is labels
            series.index += 1
            result = Result(algorithm, p_dialog.get_result()[1],  # [1] is cluster structure
                            self.norm_table.norm)
            self.result = result
            new_result = LabelsFeature(series, result)
            new_result.rename("{}".format(algorithm.name))
            self.labels_table.add_columns([new_result])
            self.update()
            self.status_bar.status()
            if not self.action_labels.isChecked():
                self.action_labels.trigger()

        p_dialog.after_finished(set_result)

    def text_report(self):
        answer = SelectFeaturesAllDialog.ask(self, self.raw_table.features, self.norm_table.features,
                                             self.labels_table.features, policy=[1])
        if answer == QDialog.Rejected:
            return
        features_raw, features_norm, features_labels = answer
        feature_labels = features_labels[0]
        labels_features = [x for x in self.labels_table.features if x!=feature_labels]
        report = Report(feature_labels.series)
        norm_data = pd.concat([f.series for f in features_norm], axis=1)
        raw_data = []
        for f in features_raw:
            if f.is_nominal:
                raw_data.extend(f.expose_one_hot())
            else:
                raw_data.append(f)
        raw_data = pd.concat([f.series for f in raw_data], axis=1)
        TextReportDialog.ask(self, feature_labels.result, report, norm_data, raw_data, labels_features, self.raw_table.features)

    def table_report(self):
        from report_dialog.table_report import TableDialog
        TableDialog.ask(self, self.result)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = ECT()
    widget.show()
    sys.exit(app.exec_())
