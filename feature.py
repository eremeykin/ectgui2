from math import sqrt
import pandas as pd


class Feature:
    def __init__(self, series, name=None, parent=None, marks=None):
        self.series = series
        self.mark = marks
        self.name = series.name if name is None else name
        try:
            pd.to_numeric(series)
            self.is_nominal = False
        except ValueError:
            self.is_nominal = True
            self.unique_values = series.unique()
            self.unique_values_num = len(series.unique())


    @classmethod
    def from_data_frame(cls, df):
        res = []
        for column in df.columns:
            res.append(cls(df[column]))
        return res

    def expose_one_hot(self):
        res = []
        if len(self.series) == 0:
            return res
        for uv in self.unique_values:
            new_col = pd.Series(data=0, index=self.series.index)
            new_col[self.series == uv] = 1
            f = Feature(new_col, name=self.series.name + str('[' + uv + ']'))
            f.is_nominal = True
            f.unique_values = self.unique_values
            f.unique_values_num = self.unique_values_num
            res.append(f)
            if len(self.unique_values) == 2:
                break
        return res

    def __hash__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __getitem__(self, item):
        return self.series[item]

    def __len__(self):
        return len(self.series)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "Feature {}".format(self.name)
