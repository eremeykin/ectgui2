from math import sqrt
import pandas as pd


class Feature:
    markers_dct = {x: None for x in ["X", "Y", "C", "A"]}

    def __init__(self, series, name=None, is_norm=False, markers=set(), parent=None):
        self.series = series
        self.name = series.name if name is None else name
        self.is_norm = is_norm
        # self._markers = markers # important! do not delete (see Normalization apply)
        # # self.add_markers(markers)

        self._markers = set()
        self.add_markers(markers)

        self.parent = parent
        try:
            pd.to_numeric(series)
            self.is_nominal = False
        except ValueError:
            self.is_nominal = True
            self.unique_values = series.unique()
            self.unique_values_num = len(series.unique())

    def rename(self, new_name):
        self.name = new_name
        self.series = self.series.rename(new_name)

    @classmethod
    def copy(cls, feature, is_norm=None):
        if is_norm is None:
            return cls(feature.series, name=feature.name, is_norm=feature.is_norm)
        else:
            return cls(feature.series, name=feature.name, is_norm=is_norm)

    @property
    def markers(self):
        return [m for m, f in Feature.markers_dct.items() if f == self]
        # return frozenset(self._markers)

    def add_markers(self, markers):
        for marker in markers:
            Feature.markers_dct[marker] = self

    @staticmethod
    def remove_markers(markers, all=False):
        if all:
            Feature.remove_markers(Feature.markers_dct.keys())
        else:
            for marker in markers:
                Feature.markers_dct[marker] = None

    @staticmethod
    def marked(marker):
        return Feature.markers_dct[marker]

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
            name = self.series.name + str('[' + uv + ']')
            new_col = pd.Series(data=0, index=self.series.index, name=name)
            new_col[self.series == uv] = 1
            f = Feature(new_col, name=name, is_norm=norm, parent=self)
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
        if other is None:
            return False
        return self.is_norm == other.is_norm and self.name == other.name

    def __getitem__(self, item):
        return self.series.iat[item]

    def __len__(self):
        return len(self.series)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "Feature {}".format(self.name)


class LabelsFeature(Feature):
    def __init__(self, series, result, name=None, is_norm=False, markers=set(), parent=None):
        super(LabelsFeature, self).__init__(series, name, is_norm, markers, parent)
        self._result = result

    @property
    def result(self):
        return self._result

    @result.setter
    def set_result(self, value):
        self._result = value
