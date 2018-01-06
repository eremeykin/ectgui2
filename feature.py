from math import sqrt
import pandas as pd


class Feature:
    def __init__(self, series, name=None, is_norm=False, markers=set()):
        self.series = series
        self.name = series.name if name is None else name
        self.is_norm = is_norm
        self._markers = markers
        try:
            pd.to_numeric(series)
            self.is_nominal = False
        except ValueError:
            self.is_nominal = True
            self.unique_values = series.unique()
            self.unique_values_num = len(series.unique())

    @classmethod
    def copy(cls, feature):
        return cls(feature.series, name=feature.name, is_norm=feature.is_norm)

    @property
    def markers(self):
        return frozenset(self._markers)

    def add_markers(self, markers):
        self._markers.update(markers)

    def remove_markers(self, markers, all=False):
        if all:
            self._markers = set()
        else:
            self._markers = self._markers - markers

    @classmethod
    def from_data_frame(cls, df):
        res = []
        for column in df.columns:
            res.append(cls(df[column]))
        return res

    def expose_one_hot(self, norm=False):
        res = []
        if len(self.series) == 0:
            return res
        for uv in self.unique_values:
            new_col = pd.Series(data=0, index=self.series.index)
            new_col[self.series == uv] = 1
            f = Feature(new_col, name=self.series.name + str('[' + uv + ']'), is_norm=norm)
            f.is_nominal = True
            f.unique_values = self.unique_values
            f.unique_values_num = self.unique_values_num
            res.append(f)
            if len(self.unique_values) == 2:
                break
        return res

    def __hash__(self):
        return hash("{} {}".format(self.name, self.is_norm))

    def __eq__(self, other):
        return self.is_norm == other.is_norm and self.name == other.name

    def __getitem__(self, item):
        return self.series[item]

    def __len__(self):
        return len(self.series)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "Feature {}".format(self.name)
