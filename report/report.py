import numpy as np
from sklearn.metrics.cluster import adjusted_rand_score as sklearn_ari
from clustering.agglomerative.utils.choose_p import ChooseP


class Report:
    class Cluster:
        def __init__(self, report, labels, symbol):
            self.report = report
            self.labels = labels
            self.symbol = symbol
            self.filter_ = self.labels == self.symbol
            self.power = self.filter_.sum()

        def elements(self, data_df):
            return data_df[self.filter_]

        def centroid(self, data_df):
            return data_df[self.filter_].mean(axis=0)

        def contribution(self, data_df):
            data_matrix = data_df.as_matrix()
            data_scatter = np.sum(data_matrix * data_matrix)
            centroid = self.centroid(data_df)
            contribution = 100 * self.power * (centroid.dot(centroid)) / data_scatter
            return contribution

        def contribution_by_features(self, data_df):
            data_matrix = data_df.as_matrix()
            data_scatter = np.sum(data_matrix * data_matrix)
            centroid = self.centroid(data_df)
            contribution = 100 * (self.power * centroid ** 2) / data_scatter
            return contribution

        def large(self, df, threshold):
            g_mean = self.report.centroid(df)
            diff = self.centroid(df) - g_mean
            diff_relative = diff / g_mean
            result = []
            for feature_name, diff_relative_value in diff_relative.iteritems():
                if diff_relative_value > threshold:
                    result.append(feature_name)
            return result

        def small(self, df, threshold):
            g_mean = self.report.centroid(df)
            diff = self.centroid(df) - g_mean
            diff_relative = diff / g_mean
            result = []
            for feature_name, diff_relative_value in diff_relative.iteritems():
                if -diff_relative_value > threshold:
                    result.append(feature_name)
            return result

    def __init__(self, labels_series):
        self.labels = labels_series
        self._clusters = None

    @property
    def clusters(self):
        if self._clusters is None:
            clusters = []
            for symbol in self.labels.unique():
                clusters.append(Report.Cluster(self, self.labels, symbol))
            self._clusters = sorted(clusters, key=lambda c: c.symbol)
            return clusters
        else:
            return self._clusters

    @property
    def clusters_number(self):
        return len(self.clusters)

    def centroid(self, df):
        return df.mean(axis=0)

    def contribution(self, df):
        c = 0
        for cluster in self.clusters:
            c += cluster.contribution(df)
        return c

    def feature_contribution(self, df):
        df_2 = df ** 2
        data_scatter = df_2.values.sum()
        return df_2.sum(axis=0) / data_scatter

    def ari(self, true_series):
        return sklearn_ari(true_series.as_matrix(), self.labels.as_matrix())

    def sw(self, cluster_structure):
        SW = ChooseP.AvgSilhouetteWidthCriterion()
        return SW(cluster_structure)
