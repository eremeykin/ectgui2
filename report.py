import numpy as np


class Report:
    THRESHOLD = 0.30

    class RichTextBuilder:

        def __init__(self, font_size=14):
            self.text = list()
            self.font_size = font_size

        def line(self, text="", bold=False, tab=0, length=None):
            if length:
                l = ("{tab}{:" + str(length) + "txt}").format(tab="&nbsp;" * tab, txt=text)
            else:
                l = "{tab}{txt}".format(tab=" " * 4 * tab, txt=text)
            if bold:
                l = "<b>{line}</b>".format(line=l)
            self.text.append(l)

        def build(self):
            res = [x.replace("\n", "") for x in self.text]
            res = [x.replace(" ", "&nbsp;") for x in res]
            res = [x.replace("_", " ") for x in res]
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

    @staticmethod
    def _color_array(array, conditions, colors):
        txt = []
        for elem in array:
            def color_elem(elem=elem, txt=txt):
                for condition, color in zip(conditions, colors):
                    if condition(elem):
                        txt.append('<font_color="{}">{}</font>'.format(color, elem))
                        return True
                return False

            if not color_elem():
                txt.append("{}".format(elem))
        return txt

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
        txt.line('Clusters characteristics:', bold=True)
        self._abstr_characteristics("I. Normalized data", self._cs.data, lambda c: c.centroid )
        l, s = self._abstr_characteristics("II. Non-normalized data", np.array([f.series for f in self.features]).T,
                                    lambda c: self.r_norm.apply(c.centroid), True)
        self._description(l,s)

        # self._normalized()
        # self._non_normalized()

    def _normalized(self):
        txt = self.txt
        max_width = max([len(x.name) for x in self.features])
        max_width = max(12, max_width) + 2
        txt.line()
        txt.line(
            'I. Normalized data              {}'.format(
                ",".join([("{:>" + str(max_width) + "}").format(x.name) for x in self.features])),
            bold=True)
        g_mean = self._cs.data.mean(axis=0)
        contribs = []
        col = "{: >" + str(max_width) + ".3}"
        for index, cluster in enumerate(self._cs.clusters):
            txt.line("cluster #{} ({} entities):".format(index + 1, cluster.power), tab=1)
            txt.line("{:24}{}".format("center:", ",".join([col.format(x) for x in cluster.centroid])), tab=2)
            diff = cluster.centroid - g_mean
            txt.line("{:24}{}".format("difference:", ",".join([col.format(x) for x in diff])), tab=2)
            contribution = 100 * cluster.power * \
                           (cluster.centroid @ cluster.centroid[None].T) / (np.sum(self._cs.data * self._cs.data))
            contribs.append(contribution)
            txt.line(("{:24}" + col).format("cluster contrib., %:", contribution[0]), tab=2)
        txt.line("total ({} entities):".format(sum([c.power for c in self._cs.clusters])), tab=1)
        txt.line("{:24}{}".format("grand mean:", ",".join([col.format(x) for x in g_mean])), tab=2)
        txt.line(("{:24}" + col).format("contribution, %:", sum(contribs)[0]), tab=2)

    def _non_normalized(self):
        txt = self.txt
        max_width = max([len(x.name) for x in self.features])
        max_width = max(12, max_width) + 2
        txt.line()
        txt.line('II. Non-normalized data         {}'.format(
            ",".join([("{:>" + str(max_width) + "}").format(x.name) for x in self.features])),
            bold=True)
        data = np.array([f.series for f in self.features])
        g_mean = data.mean(axis=1)
        contribs = []
        large_features = []
        small_features = []
        col = "{: >" + str(max_width) + ".3}"
        for index, cluster in enumerate(self._cs.clusters):
            # description = Report.RichTextBuilder()
            txt.line("cluster #{} ({} entities):".format(index + 1, cluster.power), tab=1)
            centroid = self.r_norm.apply(cluster.centroid)
            txt.line("{:24}{}".format("center:", ",".join([col.format(x) for x in centroid])), tab=2)
            diff = centroid - g_mean
            txt.line("{:24}{}".format("difference:", ",".join([col.format(x) for x in diff])), tab=2)
            diff_relative = diff / g_mean
            colored = self._color_array([col.format(x) for x in diff_relative],
                                        [lambda elem: float(elem) > Report.THRESHOLD,
                                         lambda elem: -float(elem) > Report.THRESHOLD],
                                        ['red', 'blue'])
            txt.line("{:24}{}".format("difference, %:", ",".join(colored)),
                     tab=2)
            contribution = 100 * cluster.power * (centroid @ centroid[None].T) / (np.sum(data * data))
            contribs.append(contribution)
            txt.line(("{:24}" + col).format("cluster contrib., %:", contribution[0]), tab=2)
            large_features.append(np.array(self.features)[diff_relative > Report.THRESHOLD])
            small_features.append(np.array(self.features)[-diff_relative > Report.THRESHOLD])

        txt.line("total ({} entities):".format(sum([c.power for c in self._cs.clusters])), tab=1)
        txt.line("{:24}{}".format("grand mean:", ",".join([col.format(x) for x in g_mean])), tab=2)
        txt.line(("{:24}" + col).format("contribution, %:", sum(contribs)[0]), tab=2)

    def _abstr_characteristics(self, title, data, centroid_fun, add_diff_relative=False):
        txt = self.txt
        max_width = max([len(x.name) for x in self.features])
        max_width = max(12, max_width) + 2
        txt.line()
        txt.line('{:32}{}'.format(title,
                                  ",".join([("{:>" + str(max_width) + "}").format(x.name) for x in self.features])),
                 bold=True)
        g_mean = data.mean(axis=0)
        contribs = []
        large_features = []
        small_features = []
        col = "{: >" + str(max_width) + ".3}"
        for index, cluster in enumerate(self._cs.clusters):
            txt.line("cluster #{} ({} entities):".format(index + 1, cluster.power), tab=1)

            centroid = centroid_fun(cluster)
            txt.line("{:24}{}".format("center:", ",".join([col.format(x) for x in centroid])), tab=2)

            diff = centroid - g_mean
            txt.line("{:24}{}".format("difference:", ",".join([col.format(x) for x in diff])), tab=2)
            if add_diff_relative:
                diff_relative = diff / g_mean
                colored = self._color_array([col.format(x) for x in diff_relative],
                                            [lambda elem: float(elem) > Report.THRESHOLD,
                                             lambda elem: -float(elem) > Report.THRESHOLD],
                                            ['red', 'blue'])
                txt.line("{:24}{}".format("difference, %:", ",".join(colored)), tab=2)
                large_features.append(np.array(self.features)[diff_relative > Report.THRESHOLD])
                small_features.append(np.array(self.features)[-diff_relative > Report.THRESHOLD])

            contribution = 100 * cluster.power * (centroid @ centroid[None].T) / (np.sum(data * data))
            contribs.append(contribution)
            txt.line(("{:24}" + col).format("cluster contrib., %:", contribution[0]), tab=2)
        txt.line("total ({} entities):".format(sum([c.power for c in self._cs.clusters])), tab=1)
        txt.line("{:24}{}".format("grand mean:", ",".join([col.format(x) for x in g_mean])), tab=2)
        txt.line(("{:24}" + col).format("contribution, %:", sum(contribs)[0]), tab=2)
        return large_features, small_features

    def _description(self, large_features,small_features):
        txt = self.txt
        txt.line()
        txt.line('Clusters description:', bold=True)
        i_large = iter(large_features)
        i_small = iter(small_features)
        for index, cluster in enumerate(self._cs.clusters):
            large = next(i_large)
            small = next(i_small)
            txt.line("cluster #{} ({} entities):".format(index + 1, cluster.power), tab=1)
            txt.line('features significantly ({}%) larger than average : {}'.format(Report.THRESHOLD * 100,
                                                                                    ", ".join(x.name for x in large)),
                     tab=2)
            txt.line('features significantly ({}%) smaller than average: {}'.format(Report.THRESHOLD * 100,
                                                                                    ", ".join(x.name for x in small)),
                     tab=2)

    def text(self):
        txt = list()
        tab = " " * 8
        self._header()
        # TODO implement
        # txt.append('Anomalous pattern cardinality to discard: ' + str(self.apc if self.apc is not None else 'N/A'))
        self._characteristics()
        # self._description()
        txt.append('<b>All features involved:</b>')
        for feature in self.features:
            if not feature.is_nominal:
                txt.append("\t {} mean = {:10.3}; std = {:10.3};".format(feature.name, feature.series.mean(),
                                                                         feature.series.std()))
            else:
                txt.append("\t {} mean = Nominal; std = Nominal;".format(feature.name, feature.series.mean(),
                                                                         feature.series.std()))

        return self.txt.build()
