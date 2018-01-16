class StatusBar:
    def __init__(self, parent):
        self.parent = parent
        self.status_bar = parent.statusBar()
        self.status_msg = ""

    def status(self, status_msg=None):
        if status_msg is not None:
            self.status_msg = status_msg
            # status_msg = self.status_bar.currentMessage()
        enabled = self.parent.qt_settings.value("NormEnabled", type=bool)
        enabled = "enabled" if enabled else "disabled"
        center = self.parent.qt_settings.value('Center', type=str)
        spread = self.parent.qt_settings.value('Spread', type=str)
        power = self.parent.qt_settings.value('Power', type=str)
        norm_str = "Normalization: {}, center: {}, spread: {}".format(enabled, center, spread)
        if power is not None and power != "":
            norm_str += ", mink power: {:8.4}".format(power)
        self.status_bar.showMessage("Status: {:<50} {}".format(self.status_msg, norm_str))
