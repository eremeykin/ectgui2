import numpy as np


class Report:
    def __init__(self, cluster_structure, algorithm, normalization, features):
        self._cs = cluster_structure
        self.algorithm = algorithm
        self.normalization = normalization
        self.features = features

    def text(self):
        txt = list()
        tab = " " * 8
        txt.append('<b>Intelligent clustering resulted in {} clusters;</b>'.format(self._cs.clusters_number))
        txt.append('Algorithm used: {};'.format(self.algorithm))
        txt.append('Normalization:\n\t')
        txt.append("{}enabled: {}".format(tab, self.normalization.enabled).lower())
        txt.append("{}center:  {}".format(tab, self.normalization.center).lower())
        txt.append("{}spread:  {}".format(tab, self.normalization.spread).lower())
        # TODO implement
        # txt.append('Anomalous pattern cardinality to discard: ' + str(self.apc if self.apc is not None else 'N/A'))
        txt.append('<b>Clusters characteristics:{:9}{}</b>'.format(" ", ",".join(
            ["{:>12}".format(x.name) for x in self.features])))
        txt.append('')
        txt.append('<b>I. Normalized data</b>')
        g_mean = self._cs.data.mean(axis=0)
        contribs = []
        for index, cluster in enumerate(self._cs.clusters):
            txt.append("{} cluster #{} ({} entities):".format(tab, index + 1, cluster.power))
            txt.append("{}{:18}{}".format(tab * 2, "center:",
                                          ",".join(["{: >12.3}".format(x) for x in cluster.centroid])))
            diff = cluster.centroid - g_mean
            txt.append("{}{:18}{}".format(tab * 2, "difference:", ",".join(["{: >12.3}".format(x) for x in diff])))
            contribution = 100 * cluster.power * \
                           (cluster.centroid @ cluster.centroid[None].T) / (np.sum(self._cs.data * self._cs.data))
            contribs.append(contribution)
            txt.append("{}{:18}{:12.4}".format(tab * 2, "contribution, %:", contribution[0]))
        txt.append("{} total       ({} entities):".format(tab, sum([c.power for c in self._cs.clusters])))
        txt.append("{}{:18}{}".format(tab * 2, "grand mean:", ",".join(["{: >12.3}".format(x) for x in g_mean])))
        print(sum(contribs)[0])
        txt.append("{}{:18}{:12.4}".format(tab * 2, "contribution, %:", sum(contribs)[0]))
        txt.append('')
        txt.append('<b>II. Non-normalized data</b>')
        # txt.append("{} difference,%: {}".format("  " * 8, ",".join(["{: >12.0}".format(x) for x in diff / g_mean * 100])))
        # txt.append("{} grand mean:   {}".format("  " * 8, ",".join(["{: >12.3}".format(x) for x in g_mean])))

        txt.append('<b>All features involved:</b>')
        for feature in self.features:
            if not feature.is_nominal:
                txt.append("\t {} mean = {:10.3}; std = {:10.3};".format(feature.name, feature.series.mean(),
                                                                         feature.series.std()))
            else:
                txt.append("\t {} mean = Nominal; std = Nominal;".format(feature.name, feature.series.mean(),
                                                                         feature.series.std()))

        txt = [x.replace("\n", "") for x in txt]
        txt = [x.replace(" ", "&nbsp;") for x in txt]
        formated_txt = list()
        formated_txt.append('<span style=" font-size:14pt;" >')
        formated_txt.extend(txt)
        formated_txt.append('</span>')
        return '\n<br>'.join(formated_txt)
