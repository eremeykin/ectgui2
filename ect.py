import logging.config
import sys

logging.config.fileConfig('logging.ini')

from norm_settings_dialog.norm_settings_dialog import NormSettingDialog
from feature import Feature
import numpy as np
import pandas as pd
from status_bar.status_bar import StatusBar
from tables.raw_table import RawTable
from tables.norm_table import NormTable
from select_features_dialog.select_features_dialog import SelectFeaturesDialog
from generator_dialog.generator_dialog import GeneratorDialog
from save_labels_dialog.save_labels_dialog import SaveLabelsDialog
from itertools import cycle
from report_dialog.text_report import TextReportDialog
from report import Report
from algorithms import *
from settings import Settings
from progress_gialog.progress_dialog import ProgressDialog

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
        self.action_clear_normalized.triggered.connect(self.clear_normalized)
        self.action_generate.triggered.connect(self.generate)
        self.action_by_markers.triggered.connect(self.plot_by_markers)
        self.action_svd_raw.triggered.connect(lambda: self.svd(self.raw_table))
        self.action_svd_normalized.triggered.connect(lambda: self.svd(self.norm_table))
        self.action_remove_markers.triggered.connect(self.remove_markers)
        # algorithms actions
        self.action_a_ward.triggered.connect(lambda x: self.run_algorithm(AWardAlgorithm))
        self.action_a_ward_pb.triggered.connect(lambda x: self.run_algorithm(AWarbPBAlgorithm))
        self.action_bikm_r.triggered.connect(lambda x: self.run_algorithm(BiKMeansRAlgorithm))
        self.action_depddp.triggered.connect(lambda x: self.run_algorithm(DEPDDPAlgorithm))
        self.action_ik_means.triggered.connect(lambda x: self.run_algorithm(IKMeansAlgorithm))

        self.action_norm_panel.triggered.connect(lambda: self.save_panel(self.norm_table))
        self.action_raw_panel.triggered.connect(lambda: self.save_panel(self.raw_table))
        self.action_save_text_report.triggered.connect(lambda: self.save_text_report())

        self.action_text_report.triggered.connect(self.text_report)
        self.action_table_report.triggered.connect(self.table_report)
        self.status_bar = StatusBar(self)
        self.report = None
        self.raw_table = RawTable(self.table_view_raw, self)
        self.norm_table = NormTable(self.table_view_norm, self)
        self.load_thread = None
        self.status_bar.status("Ready")
        if self.app_settings.last_loaded_file and ECT.load_last:
            self.open(self.app_settings.last_loaded_file)

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

        progress = "Load data from file: {}".format(file_name)
        self.status_bar.status(progress)
        p_dialog = ProgressDialog(self, progress, load_data, autofininsh=True)
        p_dialog.run()
        p_dialog.after_finished(lambda: self.raw_table.set_features(Feature.from_data_frame(self.data)))
        p_dialog.after_finished(lambda: setattr(self.app_settings, 'last_loaded_file', file_name))
        p_dialog.after_finished(lambda: self.setWindowTitle("INDACT: {}".format(file_name)))
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

    def save_panel(self, table):
        features = SelectFeaturesDialog.ask(self, table.all_features)
        if features == QDialog.Rejected or len(features) < 1:
            return
        res = QMessageBox.question(self, '', "Would you like add index?", QMessageBox.Yes | QMessageBox.No)
        if res != QMessageBox.Yes and res != QMessageBox.No:
            return
        f_list = []
        for f in features:
            if f.name == "cluster":
                try:
                    cluster_series = f.series.astype(int)
                    cluster_series = cluster_series.rename("cluster")
                    f_list.append(cluster_series)
                except ValueError:
                    self._mbox("Skip", "cluster feature will be skipped")
            else:
                f_list.append(f.series)

        result = pd.concat(f_list, axis=1)
        if res == QMessageBox.Yes:
            index = pd.Series(result.index, name="index", dtype=int)
            index.index += 1
            result = pd.concat([index, result], axis=1)
        self.save(result)

    def save_text_report(self):
        if self.report is None:
            self._mbox("No report", "There is no report available")
            return
        selected_features = SelectFeaturesDialog.ask(self, self.report.norm_features)
        if selected_features == QDialog.Rejected:
            return
        file_name, filter_ = QFileDialog.getSaveFileName(self, 'Save text report', 'clustering-report',
                                                         "Text file (*.txt);;Web page html file (*.html)")
        if not file_name:
            return
        if "(*.txt)" in filter_:
            self._save_txt_report(file_name + ".txt", selected_features)
        if "(*.html)" in filter_:
            self._save_html_report(file_name, selected_features)

    def _save_txt_report(self, file_name, selected_features):
        with open(file_name, 'w') as report_file:
            report_file.writelines(self.report.text(selected_features, plain=True))

    def _save_html_report(self, file_name, selected_features):
        if not os.path.exists(file_name):
            os.makedirs(file_name)
        with open(os.path.sep.join([file_name, 'index.html']), 'w') as report_file:
            report_file.writelines(self.report.text(selected_features, plain=False))
        data = np.array([f.series for f in selected_features]).T
        fig, ax = plt.subplots(figsize=(20, 10))
        fig.tight_layout()
        plot_svd(ax, data, labels=self.norm_table.cluster_feature.series, title="SVD plot", normalize=False)
        plt.savefig(os.path.sep.join([file_name, 'svd.png']))

    def remove_markers(self):
        features = self.all_features()
        for f in features:
            f.remove_markers(None, all=True)
        self.update()

    def svd(self, table):
        if not table.features:
            return self._mbox("No features", "There are no features to plot")
        features = SelectFeaturesDialog.ask(self, table.actual_features)
        if features == QDialog.Rejected:
            return
        ax = plt.gca()
        c = None
        for f in self.all_features():
            if 'C' in f.markers:
                c = f.series
        data = np.array([f.series for f in features]).T
        plot_svd(ax, data, labels=c, title="SVD plot", normalize=False)
        plt.show()

    def normalize(self):
        self.app_settings.norm_enabled = self.action_normalize.isChecked()
        self.norm_table.update_norm()

    def clear_normalized(self):
        features = SelectFeaturesDialog.ask(self, self.norm_table.actual_features)
        if features == QDialog.Rejected:
            return
        self.norm_table.delete_features(features)

    def normalize_all_features(self):
        features = SelectFeaturesDialog.ask(self, self.raw_table.actual_features)
        if features == QDialog.Rejected:
            return
        self.normalize_features(features, ask_nominal=False)

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

    def run_algorithm(self, algorithm_class):
        self.norm_table.cluster_feature = None
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
            self.norm_table.cluster_feature.series = pd.Series(p_dialog.get_result()[0])
            self.norm_table.cluster_feature.series.index += 1
            self.report = Report(self, p_dialog.get_result()[1], algorithm, self.norm_table.norm,
                                 self.norm_table.features, algorithm.time)
            self.update()
            self.status_bar.status()

        p_dialog.after_finished(set_result)

    def text_report(self):
        selected_features = SelectFeaturesDialog.ask(self, self.report.norm_features)
        if selected_features == QDialog.Rejected:
            return
        TextReportDialog.ask(self, self.report, selected_features)

    def table_report(self):
        from report_dialog.table_report import TableDialog
        TableDialog.ask(self, self.report)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = ECT()
    widget.show()
    sys.exit(app.exec_())
