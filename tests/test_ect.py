from time import sleep
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from ect import ECT

ECT.load_last = False
from norm_settings_dialog.norm_settings_dialog import NormSettingDialog
from select_features_dialog.select_features_dialog import SelectFeaturesDialog
from parameters_dialog.a_ward_dialog import AWardParamsDialog


def test_open_huge(qtbot, mock, data_file):
    window = ECT()
    qtbot.addWidget(window)
    # window.show()
    window.showMaximized()
    qtbot.waitForWindowShown(window)
    mock.patch.object(QFileDialog, 'getOpenFileName',
                      return_value=(data_file, "*.txt"))
    assert window.raw_table.features is None or len(window.raw_table.features) == 0
    qtbot.mouseClick(window.menuFile, Qt.LeftButton)
    window.action_open.trigger()
    qtbot.waitSignal(window.load_thread.finished, timeout=10000)
    qtbot.waitUntil(lambda: len(window.raw_table.features) > 0, timeout=10000)
    assert window.raw_table.features is not None and len(window.raw_table.features) != 0
    # qtbot.stopForInteraction()


def test_settings(qtbot, mock, norm_settings):
    window = ECT()
    qtbot.addWidget(window)
    window.showMaximized()
    qtbot.waitForWindowShown(window)
    mock.patch.object(NormSettingDialog, 'ask',
                      return_value=(norm_settings.enabled, norm_settings.center,
                                    norm_settings.spread, norm_settings.power))
    window.action_settings.trigger()
    assert window.qt_settings.value("NormEnabled", type=bool) == norm_settings.enabled
    assert window.qt_settings.value("Center", type=str) == norm_settings.center
    assert window.qt_settings.value("Spread", type=str) == norm_settings.spread


def test_report(qtbot, mock, small_file):
    window = ECT()
    qtbot.addWidget(window)
    window.showMaximized()
    qtbot.waitForWindowShown(window)
    mock.patch.object(QFileDialog, 'getOpenFileName',
                      return_value=(small_file, "*.txt"))
    qtbot.mouseClick(window.menuFile, Qt.LeftButton)
    window.action_open.trigger()
    qtbot.waitSignal(window.load_thread.finished, timeout=10000)
    qtbot.waitUntil(lambda: len(window.raw_table.features) > 0, timeout=10000)
    mock.patch.object(SelectFeaturesDialog, 'ask',
                      return_value=([x for x in window.raw_table.features]))  # if not x.is_nominal
    qtbot.keyPress(window, Qt.Key_N, modifier=Qt.ControlModifier | Qt.ShiftModifier)
    mock.patch.object(AWardParamsDialog, 'ask',
                      return_value=(5, None))
    qtbot.keyPress(window, Qt.Key_1, modifier=Qt.ControlModifier)
    mock.patch.object(SelectFeaturesDialog, 'ask',
                      return_value=([x for x in window.report.norm_features]))  # if not x.is_nominal
    qtbot.keyPress(window, Qt.Key_R, modifier=Qt.ControlModifier)
    qtbot.stopForInteraction()


def _context_menu_click(table, q_point, name):
    menu = table.context_menu(q_point)
    for action in menu.actions():
        if action.text() == name:
            action.trigger()
            break
    menu.hide()
