import pandas as pd

from tables.models.features_model import FeaturesTableModel


class RawTableModel(FeaturesTableModel):
    def __init__(self, features):
        super(RawTableModel, self).__init__(features=features)
