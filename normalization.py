import pandas as pd
import numpy as np
from scipy.optimize import fmin_tnc


class Normalization:
    def __init__(self, center, range_, mink_power=None):
        self._center = center
        self._range = range_
        self._mink_power = mink_power

    @property
    def center(self):
        return self._center

    @property
    def range(self):
        return self._range
    
    @property
    def mink_power(self):
        return self._mink_power

    def apply(self, data):
        if isinstance(data, pd.Series):
            return self._apply(data)
        if isinstance(data, pd.DataFrame):
            return data.apply(lambda x: self._apply(x))

        raise Exception('Wrong data type for normalization')

    def _get_center(self, series):
        if self._center == "No centring":
            center = 0
        elif self._center == "Minimum":
            center = series.min()
        elif self._center == "Mean":
            center = series.mean()
        elif self._center == "Median":
            center = series.median()
        elif self._center == "Minkowski center":
            def D(X, a):
                return np.sum(np.abs(X - a) ** self._mink_power) / len(X)

            center = fmin_tnc(func=lambda x: D(series, x), x0=np.mean(series), approx_grad=True)[0]
        else:
            raise Exception('Unknown center type')
        return center

    def _get_rng(self, series):
        if self._range == "None":
            rng = 1
        elif self._range == "Semi range":
            rng = (series.max() - series.min()) / 2
        elif self._range == "Standard deviation":
            rng = series.std()
        elif self._range == "Absolute deviation":
            rng = ((series - series.median()).abs()).mean()
        else:
            raise Exception('Unknown range type')
        return rng

    def _apply(self, series):
        center = self._get_center(series)
        rng = self._get_rng(series)
        result = (series - center) / rng
        return result

    def __bool__(self):
        return True

