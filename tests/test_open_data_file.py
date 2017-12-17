from time import sleep
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from ect import ECT


def test_open_huge(qtbot, mock, data_file):
    window = ECT()
    qtbot.addWidget(window)
    # window.show()
    window.showMaximized()
    qtbot.waitForWindowShown(window)
    mock.patch.object(QFileDialog, 'getOpenFileName',
                      return_value=(data_file, "*.txt"))
    assert window._raw_data is None
    qtbot.mouseClick(window.menuFile, Qt.LeftButton)
    window.actionOpen.trigger()
    qtbot.waitSignal(window.load_thread.finished, timeout=10000)
    qtbot.waitUntil(lambda: window._raw_data is not None, timeout=10000)
    assert window._raw_data is not None
    # qtbot.stopForInteraction()
