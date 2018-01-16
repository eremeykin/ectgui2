import pandas as pd
import numpy as np
from scipy.optimize import fmin_tnc
from math import sqrt
from feature import Feature

class Normalization:
    def __init__(self, enabled, center, spread, mink_power=None):
        self._mink_power = mink_power
        self.spread_dict = {"None": lambda series: 1,
                           "Semi range": lambda series: (series.max() - series.min()) / 2,
                           "Standard deviation": lambda series: series.std(),
                           "Absolute deviation": lambda series: ((series - series.median()).abs()).mean()}

        self.center_dict = {"No centring": lambda series: 0,
                            "Minimum": lambda series: series.min(),
                            "Mean": lambda series: series.mean(),
                            "Median": lambda series: series.median(),
                            "Minkowski center": lambda series:
                            fmin_tnc(func=lambda c: np.sum(np.abs(series - c) ** self._mink_power) / len(series),
                                     x0=np.mean(series), approx_grad=True, disp=0)[0]}
        self._center_name = center
        self._spread_name = spread
        self._center = self.center_dict[center]
        self._spread = self.spread_dict[spread]
        self._enabled = enabled

    @property
    def enabled(self):
        return self._enabled

    @property
    def center(self):
        return self._center_name

    @property
    def spread(self):
        return self._spread_name

    @property
    def mink_power(self):
        return self._mink_power

    def apply(self, feature):
        if self._enabled:
            series = feature.series
            res = (series - self._center(series)) / self._spread(series)
            if feature.is_nominal:
                res /= sqrt(feature.unique_values_num)
            return Feature(res, name=feature.name, is_norm=True, markers=feature.markers)
        else:
            return feature

    def reverse(self, point, features):
        if self.enabled:
            return
        else:
            return
