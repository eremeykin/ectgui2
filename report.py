import numpy as np


class Report:
    class RichTextBuilder:

        def __init__(self, font_size=14):
            self.text = list()
            self.font_size = font_size

        def line(self, text="", bold=False, tab=0, length=None):
            if length:
                l = ("{tab}{:" + str(length) + "txt}").format(tab=" " * tab, txt=text)
            else:
                l = "{tab}{txt}".format(tab=" " * 4 * tab, txt=text)
            if bold:
                l = "<b>{line}</b>".format(line=l)
            self.text.append(l)

        def build(self):
            res = [x.replace("\n", "") for x in self.text]
            res = [x.replace(" ", "&nbsp;") for x in res]
            formated_res = list()
            formated_res.append('<span style=" font-size:{fs}pt;" >'.format(fs=self.font_size))
            formated_res.extend(res)
            formated_res.append('</span>')
            return '\n<br>'.join(formated_res)

    def __init__(self, cluster_structure, algorithm, normalization, features):
        self._cs = cluster_structure
        self.algorithm = algorithm
        self.normalization = normalization
        self.features = features
        self.r_norm = normalization.reverse(features)
        self.txt = Report.RichTextBuilder()

    def _header(self):
        txt = self.txt
        txt.line('Intelligent clustering resulted in {} clusters;'.format(self._cs.clusters_number), bold=True)
        txt.line('Algorithm used: {};'.format(self.algorithm))
        txt.line('Normalization:')
        txt.line("enabled: {}".format(self.normalization.enabled).lower(), tab=1)
        txt.line("center:  {}".format(self.normalization.center).lower(), tab=1)
        txt.line("spread:  {}".format(self.normalization.spread).lower(), tab=1)

    def _characteristics(self):
        txt = self.txt
        txt.line('Clusters characteristics: {}'.
                 format(",".join(["{:>12}".format(x.name) for x in self.features])), bold=True)

        self._normalized()
        self._non_normalized()

    def _normalized(self):
        txt = self.txt
        txt.line()
        txt.line('I. Normalized data', bold=True)
        g_mean = self._cs.data.mean(axis=0)
        contribs = []
        for index, cluster in enumerate(self._cs.clusters):
            txt.line("cluster #{} ({} entities):".format(index + 1, cluster.power), tab=1)
            txt.line("{:18}{}".format("center:", ",".join(["{: >12.3}".format(x) for x in cluster.centroid])), tab=2)
            diff = cluster.centroid - g_mean
            txt.line("{:18}{}".format("difference:", ",".join(["{: >12.3}".format(x) for x in diff])), tab=2)
            contribution = 100 * cluster.power * \
                           (cluster.centroid @ cluster.centroid[None].T) / (np.sum(self._cs.data * self._cs.data))
            contribs.append(contribution)
            txt.line("{:18}{:12.4}".format("contribution, %:", contribution[0]), tab=2)
        txt.line("total ({} entities):".format(sum([c.power for c in self._cs.clusters])), tab=1)
        txt.line("{:18}{}".format("grand mean:", ",".join(["{: >12.3}".format(x) for x in g_mean])), tab=2)
        txt.line("{:18}{:12.4}".format("contribution, %:", sum(contribs)[0]), tab=2)

    def _non_normalized(self):
        txt = self.txt
        txt.line()
        txt.line('II. Non-normalized data', bold=True)
        data = np.array([f.series for f in self.features])
        g_mean = data.mean(axis=1)
        contribs = []
        for index, cluster in enumerate(self._cs.clusters):
            txt.line("cluster #{} ({} entities):".format(index + 1, cluster.power), tab=1)
            centroid = self.r_norm.apply(cluster.centroid)
            txt.line("{:18}{}".format("center:", ",".join(["{: >12.3}".format(x) for x in centroid])), tab=2)
            diff = centroid - g_mean
            txt.line("{:18}{}".format("difference:", ",".join(["{: >12.3}".format(x) for x in diff])), tab=2)
            contribution = 100 * cluster.power * (centroid @ centroid[None].T) / (np.sum(data * data))
            contribs.append(contribution)
            txt.line("{:18}{:12.4}".format("contribution, %:", contribution[0]), tab=2)
        txt.line("total ({} entities):".format(sum([c.power for c in self._cs.clusters])), tab=1)
        txt.line("{:18}{}".format("grand mean:", ",".join(["{: >12.3}".format(x) for x in g_mean])), tab=2)
        txt.line("{:18}{:12.4}".format("contribution, %:", sum(contribs)[0]), tab=2)

    def text(self):
        txt = list()
        tab = " " * 8
        self._header()
        # TODO implement
        # txt.append('Anomalous pattern cardinality to discard: ' + str(self.apc if self.apc is not None else 'N/A'))
        self._characteristics()

        txt.append('<b>All features involved:</b>')
        for feature in self.features:
            if not feature.is_nominal:
                txt.append("\t {} mean = {:10.3}; std = {:10.3};".format(feature.name, feature.series.mean(),
                                                                         feature.series.std()))
            else:
                txt.append("\t {} mean = Nominal; std = Nominal;".format(feature.name, feature.series.mean(),
                                                                         feature.series.std()))

        return self.txt.build()
