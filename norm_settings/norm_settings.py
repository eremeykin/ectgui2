from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtGui import *
import sys
from models.raw import *
import pandas as pd
import os

ui_file = os.path.join(os.path.dirname(__file__), '../ui/norm_settings.ui')
UI_NormSettings, QtBaseClass = uic.loadUiType(ui_file)


class NormSettingDialog(UI_NormSettings, QDialog):
    def __init__(self, parent, name=None):
        super(NormSettingDialog, self).__init__(parent)
        self.setupUi(self)

