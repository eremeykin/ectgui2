import pandas as pd

from tables.models.pandas import PandasTableModel


class RawTableModel(PandasTableModel):
    def __init__(self, data=pd.DataFrame()):
        super(RawTableModel, self).__init__(data=data)
