from time import sleep
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from ect import ECT
from norm_settings_dialog.norm_settings import NormSettingDialog


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
    qtbot.waitUntil(lambda: len(window.raw_table.features)>0, timeout=10000)
    assert window.raw_table.features is not None and len(window.raw_table.features) != 0
    # qtbot.stopForInteraction()


def test_settings(qtbot, mock, norm_settings):
    window = ECT()
    qtbot.addWidget(window)
    window.showMaximized()
    qtbot.waitForWindowShown(window)
    mock.patch.object(NormSettingDialog, 'ask',
                      return_value=(norm_settings.enabled, norm_settings.center, norm_settings.range))
    window.action_settings.trigger()
    assert window.qt_settings.value("NormEnabled", type=bool) == norm_settings.enabled
    assert window.qt_settings.value("Center", type=str) == norm_settings.center
    assert window.qt_settings.value("Range", type=str) == norm_settings.range


def _context_menu_click(table, q_point, name):
    menu = table.context_menu(q_point)
    for action in menu.actions():
        if action.text() == name:
            action.trigger()
            break
    menu.hide()
