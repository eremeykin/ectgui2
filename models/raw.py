from models.pandas import PandasTableModel
import pandas as pd


class RawTableModel(PandasTableModel):
    def __init__(self, data=pd.DataFrame()):
        super(RawTableModel, self).__init__(data=data)
