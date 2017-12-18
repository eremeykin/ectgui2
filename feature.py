from math import sqrt
import pandas as pd


class Feature:
    def __init__(self, series, mark=None):
        self.series = series
        self.mark = mark
        self.name = series.name
        try:
            pd.to_numeric(series)
            self.is_nominal = False
        except ValueError:
            self.is_nominal = True
            self.unique_values_num = series.unique()

    def norm_representation(self, norm):
        res = norm.apply(pd.DataFrame(self.series))
        if self.is_nominal:
            res = res / sqrt(self.unique_values_num)
        return res

    def __len__(self):
        return len(series)