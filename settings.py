from PyQt5.QtCore import *


class Settings:
    def __init__(self):
        self.settings = QSettings("settings.ini", QSettings.IniFormat)

    @property
    def center(self):
        return self.settings.value('Center', defaultValue="Mean", type=str)

    @property
    def spread(self):
        return self.settings.value('Spread', defaultValue="Semi range", type=str)

    @property
    def norm_enabled(self):
        return self.settings.value('NormEnabled', defaultValue=True, type=bool)

    @property
    def power(self):
        return self.settings.value('Power', type=str)

    @property
    def last_loaded_file(self):
        return self.settings.value("LastLoadedFile", type=str)

    @property
    def gen_dialog_gen_seed(self):
        return self.settings.value("GeneratorDialog-GeneratorSeed", defaultValue=0, type=int)

    @property
    def gen_dialog_min_cluster_card(self):
        return self.settings.value("GeneratorDialog-MinClusterCardinality", defaultValue=10, type=int)

    @property
    def gen_dialog_number_of_clusters(self):
        return self.settings.value("GeneratorDialog-NumberOfClusters", defaultValue=5, type=int)

    @property
    def gen_dialog_features(self):
        return self.settings.value("GeneratorDialog-Features", defaultValue=6, type=int)

    @property
    def gen_dialog_number_of_objects(self):
        return self.settings.value("GeneratorDialog-NumberOfObjects", defaultValue=250, type=int)

    @property
    def gen_dialog_box_parameter(self):
        return self.settings.value("GeneratorDialog-BoxParameter", defaultValue=0.5, type=float)

    @property
    def report_settings_font(self):
        return self.settings.value("ReportSettings-Font", defaultValue=14, type=int)

    @property
    def report_settings_calc_sw(self):
        return self.settings.value("ReportSettings-CalculateSW", defaultValue=False, type=bool)

    @property
    def report_settings_threshold(self):
        return self.settings.value("ReportSettings-Threshold", defaultValue=0.30, type=float)

    @center.setter
    def center(self, value):
        self.settings.setValue('Center', value)

    @spread.setter
    def spread(self, value):
        self.settings.setValue('Spread', value)

    @norm_enabled.setter
    def norm_enabled(self, value):
        self.settings.setValue('NormEnabled', value)

    @power.setter
    def power(self, value):
        self.settings.setValue('Power', value)

    @last_loaded_file.setter
    def last_loaded_file(self, value):
        self.settings.setValue('LastLoadedFile', value)

    @gen_dialog_gen_seed.setter
    def gen_dialog_gen_seed(self, value):
        self.settings.setValue("GeneratorDialog-GeneratorSeed", value)

    @gen_dialog_min_cluster_card.setter
    def gen_dialog_min_cluster_card(self, value):
        self.settings.setValue("GeneratorDialog-MinClusterCardinality", value)

    @gen_dialog_number_of_clusters.setter
    def gen_dialog_number_of_clusters(self, value):
        self.settings.setValue("GeneratorDialog-NumberOfClusters", value)

    @gen_dialog_features.setter
    def gen_dialog_features(self, value):
        self.settings.setValue("GeneratorDialog-Features", value)

    @gen_dialog_number_of_objects.setter
    def gen_dialog_number_of_objects(self, value):
        self.settings.setValue("GeneratorDialog-NumberOfObjects", value)

    @gen_dialog_box_parameter.setter
    def gen_dialog_box_parameter(self, value):
        self.settings.setValue("GeneratorDialog-BoxParameter", value)

    @report_settings_font.setter
    def report_settings_font(self, value):
        self.settings.setValue("ReportSettings-Font", value)

    @report_settings_calc_sw.setter
    def report_settings_calc_sw(self, value):
        self.settings.setValue("ReportSettings-CalculateSW", value)

    @report_settings_threshold.setter
    def report_settings_threshold(self, value):
        self.settings.setValue("ReportSettings-Threshold", value)
