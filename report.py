import numpy as np
class Report:
    def __init__(self, cluster_structure, algorithm, normalization, features):
        self._cs = cluster_structure
        self.algorithm = algorithm
        self.normalization = normalization
        self.features = features

    def text(self):
        txt = list()
        txt.append('<b>Intelligent clustering resulted in {} clusters;</b>'.format(self._cs.clusters_number))
        txt.append('Algorithm used: {};'.format(self.algorithm))
        txt.append('Normalization:\n\t')
        txt.append("{} enabled: {}".format("  " * 4, self.normalization.enabled).lower())
        txt.append("{} center:  {}".format("  " * 4, self.normalization.center).lower())
        txt.append("{} spread:   {}".format("  " * 4, self.normalization.spread).lower())
        # TODO implement
        # txt.append('Anomalous pattern cardinality to discard: ' + str(self.apc if self.apc is not None else 'N/A'))
        txt.append('<b>Clusters characteristics:</b>')
        g_mean = self._cs.data.mean(axis=0)
        for index, cluster in enumerate(self._cs.clusters):
            txt.append("{} cluster #{}".format("  " * 4, index+1))
            txt.append("{} center:     {}".format("  " * 8, ["{: >12.3}".format(x) for x in cluster.centroid]))
            txt.append("{} grand mean:   {}".format("  " * 8, ["{: >12.3}".format(x) for x in g_mean]))
            diff = cluster.centroid - g_mean
            txt.append("{} difference:   {}".format("  " * 8, ["{: >12.3}".format(x) for x in diff]))
            txt.append("{} difference,%: {}".format("  " * 8, ["{: >12.0}".format(x) for x in diff/g_mean*100]))
            contribution = 100 * cluster.power * (cluster.centroid @ cluster.centroid[None].T)/ (np.sum(self._cs.data * self._cs.data))
            txt.append("{} contribution: {:8.4}".format("  " * 8, contribution[0]))
        txt.append('<b>All features involved:</b>')
        for feature in self.features:
            if not feature.is_nominal:
                txt.append("\t {} mean = {:10.3}; std = {:10.3};".format(feature.name, feature.series.mean(),
                                                                         feature.series.std()))
            else:
                txt.append("\t {} mean = Nominal; std = Nominal;".format(feature.name, feature.series.mean(),
                                                                         feature.series.std()))

        #
        # interp = interpretattion(self.norm_data, self.data, self.labels, self.centroids, self.norm)
        # txt.append('Cluster-specific info:')
        # for l in self.u_labels:
        #     txt.append('Cluster #' + str(l) + ' [' + str(np.count_nonzero(self.labels == l)) + ' entities]:')
        #     txt.append('\tcentroid (real): ' + str(['{0:.3f}'.format(x) for x in interp[l]['centr_real']]))
        #     txt.append('\tcentroid (norm): ' + str(['{0:.3f}'.format(x) for x in interp[l]['centr_norm']]))
        #     txt.append('\tcentroid (% over/under grand mean): ' + str(interp[l]['ovn']))
        #     txt.append(
        #         '\tcontribution (proper and cumulative): {:10.2}'.format(interp[l]['scatcl']) + ',{:10.2}'.format(
        #             interp[l]['scac']))
        #     nado, nido = [], []
        #     for f, f_name in enumerate(self.norm_data.columns):
        #         if interp[l]['ovn'][f] > 30:
        #             nado.append(f_name)
        #         if -interp[l]['ovn'][f] > 30:
        #             nido.append(f_name)
        #     txt.append('\tfeatures significantly larger than average: ' + ("None" if nado == [] else ",".join(nado)))
        #     txt.append('\tfeatures significantly smaller than average: ' + ("None" if nido == [] else ",".join(nido)))
        #     #     TODO CHANGE!!! !!!
        #     self.clusters[l] = Cluster(l, interp[l]['centr_real'], np.count_nonzero(self.labels == l))
        txt = [x.replace("\n", "") for x in txt]
        txt = [x.replace(" ", "&nbsp;") for x in txt]
        formated_txt = list()
        formated_txt.append('<span style=" font-size:14pt;" >')
        formated_txt.extend(txt)
        formated_txt.append('</span>')
        return '\n<br>'.join(formated_txt)
