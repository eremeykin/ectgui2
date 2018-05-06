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
            # es = set()
            # es.update(markers)
            # markers = es
            # Feature.remove_markers(markers)
            # for marker in markers:
            #     Feature.markers_dict[marker] = self
            # old_markers = set(self.markers)
            # old_markers.update(markers)
            # self._markers = old_markers

    @staticmethod
    def remove_markers(markers, all=False):
        if all:
            Feature.remove_markers(Feature.markers_dct.keys())
        else:
            for marker in markers:
                Feature.markers_dct[marker] = None

                # if all:
                #     all_markers = Feature.markers_dict.keys()
                #     Feature.remove_markers(all_markers)
                # else:
                #     for marker in markers:
                #         feature = Feature.markers_dict.get(marker, False)
                #         if feature:
                #             feature._markers = feature._markers - markers
                #             del Feature.markers_dict[marker]

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
            new_col = pd.Series(data=0, index=self.series.index)
            new_col[self.series == uv] = 1
            f = Feature(new_col, name=self.series.name + str('[' + uv + ']'), is_norm=norm, parent=self)
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
