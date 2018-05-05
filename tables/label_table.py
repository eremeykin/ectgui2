from tables.table import Table


class LabelTable(Table):
    def __init__(self, table_view, parent):
        super().__init__(table_view, parent, hide_scroll=True)
        self.counter = 0
        # table_view.horizontalHeader().setSectionResizeMode(1)

    def add_columns(self, columns):
        for col in columns:
            self.counter += 1
            col.rename(col.name + "({})".format(self.counter))
        super().add_columns(columns)

    def context_menu(self, point):
        menu = super().context_menu(point)
        menu.popup(self._table_view.horizontalHeader().mapToGlobal(point))
