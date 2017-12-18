from time import sleep
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from ect import ECT
from norm_settings.norm_settings import NormSettingDialog


def test_delete_raw_column(qtbot, mock, iris, table_type):
    window = ECT()
    qtbot.addWidget(window)
    window.showMaximized()
    qtbot.waitForWindowShown(window)
    mock.patch.object(QFileDialog, 'getOpenFileName',
                      return_value=(iris, "*.txt"))
    qtbot.mouseClick(window.menuFile, Qt.LeftButton)
    window.action_open.trigger()
    qtbot.waitSignal(window.load_thread.finished, timeout=10000)
    if table_type == 'raw':
        table = window.raw_table
        qtbot.waitUntil(lambda: not window.raw_table.data.empty, timeout=10000)
    else:
        table = window.norm_table
        qtbot.waitUntil(lambda: not window.raw_table.data.empty, timeout=10000)
        li_prev = 0
        x=0
        _context_menu_click(window.raw_table, QPoint(0, 0), "Normalize")
        for li in range(5):
            while True:
                x = x+1
                li = window.raw_table._table_view.horizontalHeader().logicalIndexAt(x)
                if li != li_prev:
                    _context_menu_click(window.raw_table, QPoint(x, 0), "Normalize")
                    li_prev = li
                    break
    assert table.data is not None and not window.raw_table.data.empty
    cols = len(table.data.columns)
    while len(table.data.columns) > 0:
        _context_menu_click(table, QPoint(0, 0), "Delete")
        assert len(table.data.columns) == cols - 1
        cols -= 1


def _context_menu_click(table, q_point, name):
    menu = table.context_menu(q_point)
    for action in menu.actions():
        if action.text() == name:
            action.trigger()
            break
    menu.hide()
