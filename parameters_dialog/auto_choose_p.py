import os
from PyQt5 import QtCore
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from PyQt5 import QtGui
import pandas as pd
import numpy as np
from tables.models.pandas_model import PandasTableModel

ui_file = os.path.join(os.path.dirname(__file__), '../ui/auto_choose_p.ui')
UI_AutoChoosePDialog, QtBaseClass = uic.loadUiType(ui_file)


class AutoChoosePDialog(UI_AutoChoosePDialog, QDialog):
    def __init__(self, parent):
        super(AutoChoosePDialog, self).__init__(parent)
        self.setupUi(self)
        self.clusters_number_spin.setValue(parent.clusters_number_spin.value())

    @classmethod
    def ask(cls, parent):
        dialog = cls(parent)
        if dialog.exec_() == QDialog.Accepted:
            start = float(dialog.start_spin.value())
            step = float(dialog.step_spin.value())
            end = float(dialog.end_spin.value())
            clusters_number = int(dialog.clusters_number_spin.value())
            return start, step, end, clusters_number
        return QDialog.Rejected


ui_file_table = os.path.join(os.path.dirname(__file__), '../ui/auto_choose_p_table.ui')
UI_AutoChoosePTableDialog, QtBaseClassTable = uic.loadUiType(ui_file_table)


class AutoChoosePTableDialog(UI_AutoChoosePTableDialog, QDialog):
    def __init__(self, parent, table):
        super(AutoChoosePTableDialog, self).__init__(parent)
        self.setupUi(self)
        model = ColorMaxTable(table)
        self.table_view.setModel(model)

    @classmethod
    def ask(cls, parent, table):
        dialog = cls(parent, table)
        return dialog.exec_()


class ColorMaxTable(PandasTableModel):
    def __init__(self, data=pd.DataFrame()):
        super(ColorMaxTable, self).__init__(data)
        matrix = data.as_matrix()
        mx = np.argmax(matrix)
        rows, cols = matrix.shape
        self.max_row = mx // cols
        self.max_col = mx - self.max_row * cols

    def color(self, i, j):
        if i == self.max_row and j == self.max_col:
            return QtCore.QVariant(QtGui.QColor(255, 90, 90))
        return QtCore.QVariant()
