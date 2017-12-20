from time import sleep
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from ect import ECT
from norm_settings_dialog.norm_settings_dialog import NormSettingDialog


def test_delete_raw_column(qtbot, mock, iris, table_type):
    window = ECT()
    qtbot.addWidget(window)
    window.show()
    # window.showMaximized()
    qtbot.waitForWindowShown(window)
    mock.patch.object(QFileDialog, 'getOpenFileName',
                      return_value=(iris, "*.txt"))
    qtbot.mouseClick(window.menuFile, Qt.LeftButton)
    window.action_open.trigger()
    qtbot.waitSignal(window.load_thread.finished, timeout=10000)
    mock.patch.object(QMessageBox, 'exec_',
                      return_value=QMessageBox.Ok)
    if table_type == 'raw':
        table = window.raw_table
        qtbot.waitUntil(lambda: len(window.raw_table.features) > 0, timeout=10000)
    else:
        table = window.norm_table
        qtbot.waitUntil(lambda: len(window.raw_table.features) > 0, timeout=10000)
        li_prev, li = 0, 0
        x = 0
        _context_menu_click(window.raw_table, QPoint(0, 0), "Normalize")
        while len(window.norm_table.features)<7:
            x = x + 1
            li = window.raw_table._table_view.horizontalHeader().logicalIndexAt(x)
            if li != li_prev:
                _context_menu_click(window.raw_table, QPoint(x, 2), "Normalize")
                print("Click Normalize")
                li_prev = li
                continue
            if x > 10000:
                assert False
    assert table.features is not None and window.raw_table.features
    cols = len(table.features)
    while len(table.features) > 0:
        _context_menu_click(table, QPoint(0, 0), "Delete")
        assert len(table.features) == cols - 1
        cols -= 1


def _context_menu_click(table, q_point, name):
    menu = table.context_menu(q_point)
    for action in menu.actions():
        if action.text() == name:
            action.trigger()
            break
    menu.hide()
