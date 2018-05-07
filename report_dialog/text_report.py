import os
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from report.report_html_printer import ReportHTMLPrinter
from report.report_plain_printer import ReportPlainPrinter
from report_dialog.report_settings_dialog import ReportSettingsDialog

ui_file = os.path.join(os.path.dirname(__file__), '../ui/text_report_main.ui')
UI_TextReportDialog, QtBaseClass = uic.loadUiType(ui_file)


class TextReportDialog(UI_TextReportDialog, QMainWindow):
    def __init__(self, parent, result, report, norm_data, raw_data, labels_features, all_raw_features):
        super(TextReportDialog, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.result = result
        self.report = report
        self.norm_data = norm_data
        self.raw_data = raw_data
        self.labels_features = labels_features
        self.action_save.triggered.connect(self.save_text_report)
        self.action_settings.triggered.connect(self.settings)
        # settings
        self.font_size = 14
        self.calculate_sw = False
        self.threshold = 0.30
        self.ari_features = []
        self.conv_features = []
        self.clusters_to_print = []
        self.clusters_index = None
        self.all_raw_features = all_raw_features
        self.update()

    def update(self):
        self.text_browser.setText("Updating ...")
        cluster_index = self.clusters_index.series if self.clusters_index is not None else None
        text = ReportHTMLPrinter(self.result, self.report, self.norm_data, self.raw_data,
                                 font_size=self.font_size, calculate_sw=self.calculate_sw,
                                 threshold=self.threshold, ari_series=[f.series for f in self.ari_features],
                                 print_clusters=self.clusters_to_print,
                                 clusters_index=cluster_index,
                                 conv_labels=[f.series for f in self.conv_features]).print()
        if text is None:
            self.text_browser.setText("Report is unavailable")
        else:
            self.text_browser.setText(text)
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.text_browser.setFont(font)

    def settings(self):
        clusters = [c.symbol for c in self.report.clusters]
        answer = ReportSettingsDialog.ask(self, labels_features=self.labels_features, clusters=clusters,
                                          all_raw_features=self.all_raw_features)
        if answer == QDialog.Rejected:
            return
        self.font_size, self.calculate_sw, self.threshold, self.ari_features, self.conv_features, self.clusters_to_print, self.clusters_index = answer
        self.update()

    def save_text_report(self):
        file_name, filter_ = QFileDialog.getSaveFileName(self, 'Save text report', 'clustering-report',
                                                         "Text file (*.txt);;Web page html file (*.html)")
        if not file_name:
            return
        if "(*.txt)" in filter_:
            self._save_txt_report(file_name + ".txt")
        if "(*.html)" in filter_:
            self._save_html_report(file_name + ".html")

    def _save_txt_report(self, file_name):
        with open(file_name, 'w') as report_file:
            text = ReportPlainPrinter(self.result, self.report, self.norm_data, self.raw_data).print()
            report_file.writelines(text)

    def _save_html_report(self, file_name):
        with open(file_name, 'w') as report_file:
            text = ReportHTMLPrinter(self.result, self.report, self.norm_data, self.raw_data).print()
            report_file.writelines(text)

    @classmethod
    def ask(cls, parent, result, report, norm_data, raw_data, labels_features, all_raw_features):
        dialog = cls(parent, result, report, norm_data, raw_data, labels_features, all_raw_features)
        dialog.show()
