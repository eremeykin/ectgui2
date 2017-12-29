from tables.models.features_model import FeaturesTableModel
from feature import Feature
import pandas as pd


class NormTableModel(FeaturesTableModel):
    def __init__(self, features=None, norm=None, cluster_feature=None):
        cf = []
        self.cluster_feature = cluster_feature
        if features and cluster_feature is None:
            data = list("?" * len(features[0]))
            index = features[0].series.index
            series = pd.Series(data=data, index=index, dtype=str)
            self.cluster_feature = Feature(series=series, name="Cluster #", norm=True)
            cf.append(self.cluster_feature)
        elif cluster_feature is not None:
            cf.append(cluster_feature)
        norm_features = [norm.apply(x) for x in features]
        super().__init__(features=norm_features + cf)
