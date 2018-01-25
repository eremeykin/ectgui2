import tabulate
import numpy as np
import re

tabulate._invisible_codes = re.compile(r"\x1b\[\d+[;\d]*m|\x1b\[\d*\;\d*\;\d*m|<.*>")

tabulate_old = tabulate.tabulate
_visible_width_old = tabulate._visible_width
_strip_invisible_old = tabulate._strip_invisible


def _strip_invisible(s):
    "Remove invisible ANSI color codes."
    try:
        s = re.sub(r'<.*?>', '', s)
        s = re.sub('&nbsp;', ' ', s)
    except:
        pass
    return _strip_invisible_old(s)


tabulate._strip_invisible = _strip_invisible


def _visible_width(s):
    try:
        s = re.sub(r'<.*?>', '', s)
        s = re.sub('&nbsp;', ' ', s)
    except:
        pass
    return _visible_width_old(s)


tabulate._visible_width = _visible_width


def tabulate(*args, **kwargs):
    res = tabulate_old(*args, **kwargs)
    res = res.replace("\n", "<br>")
    return res


tabulate.tabulate = tabulate


class Report:
    THRESHOLD = 0.30
    TAB = "&nbsp;" * 4

    class RichTextBuilder:

        def __init__(self, font_size=14):
            self.text = list()
            self.font_size = font_size

        def line(self, text="", bold=False, tab=0, length=None):
            if length:
                l = ("{tab}{:" + str(length) + "txt}").format(tab=Report.TAB * tab, txt=text)
            else:
                l = "{tab}{txt}".format(tab=" " * 4 * tab, txt=text)
            if bold:
                l = "<b>{line}</b>".format(line=l)
            self.text.append(l)

        def build(self):
            res = [x.replace("\n", "") for x in self.text]
            res = [x.replace(" ", "&nbsp;") for x in res]
            res = [x.replace("_", " ") for x in res]  # see <font_color="red">
            formated_res = list()
            formated_res.append('<span style=" font-size:{fs}pt;" >'.format(fs=self.font_size))
            formated_res.extend(res)
            formated_res.append('</span>')
            return '\n<br>'.join(formated_res)

    def __init__(self, cluster_structure, algorithm, normalization, norm_features, time):
        self._cs = cluster_structure
        self.algorithm = algorithm
        self.normalization = normalization
        self.norm_features = norm_features
        self.r_norm = normalization.reverse(norm_features)
        self.txt = Report.RichTextBuilder()
        self.time = time

    @property
    def cluster_structure(self):
        return self._cs

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
        txt.line('Algorithm used: {}, ({:.3} s);'.format(self.algorithm, self.time))
        txt.line('Normalization:')
        txt.line("enabled: {}".format(self.normalization.enabled).lower(), tab=1)
        txt.line("center:  {}".format(self.normalization.center).lower(), tab=1)
        txt.line("spread:  {}".format(self.normalization.spread).lower(), tab=1)

    def _characteristics(self):
        txt = self.txt
        txt.line('Clusters characteristics:', bold=True)
        self._abstr_characteristics("I. Normalized data", self._cs.data, lambda c: c.centroid)
        l, s = self._abstr_characteristics("II. Non-normalized data",
                                           np.array([f.series for f in self.norm_features]).T,
                                           lambda c: self.r_norm.apply(c.centroid), True)
        self._description(l, s)

    def _abstr_characteristics(self, title, data, centroid_fun, add_diff_relative=False):
        txt = self.txt
        tab = "&nbsp;" * 4
        headers = ["<b>{}</b>".format(title)] + ["<b>{}</b>".format(f.name) for f in self.norm_features]
        table = []
        table += []
        g_mean = data.mean(axis=0)
        contribs = []
        large_features = []
        small_features = []
        for index, cluster in enumerate(self._cs.clusters):
            table += [["{}cluster #{} ({} entities):".format(tab, index + 1, cluster.power)]]
            centroid = centroid_fun(cluster)
            table += [["{}center".format(tab * 2)] + [x for x in centroid]]
            # diff
            diff = centroid - g_mean
            table += [["{}difference:".format(tab * 2)] + [x for x in diff]]
            if add_diff_relative:
                diff_relative = 100 * diff / g_mean
                colored = self._color_array([x for x in diff_relative],
                                            [lambda elem: float(elem) > 100 * Report.THRESHOLD,
                                             lambda elem: -float(elem) > 100 * Report.THRESHOLD],
                                            ['red', 'blue'])
                table += [["{}difference, %:".format(tab * 2)] + colored]
                large_features.append(np.array(self.norm_features)[diff_relative > Report.THRESHOLD])
                small_features.append(np.array(self.norm_features)[-diff_relative > Report.THRESHOLD])
            # cluster contribution
            contribution = 100 * cluster.power * (centroid @ centroid[None].T) / (np.sum(data * data))
            contribs.append(contribution)
            table += [["{}cluster contrib., %:".format(tab * 2)] + list(contribution)]

        table += [["{}total ({} entities):".format(tab, sum([c.power for c in self._cs.clusters]))]]
        table += [["{}{}".format(tab * 2, "grand mean:")] + [x for x in g_mean]]
        table += [["{}{}".format(tab * 2, "contribution, %:")] + list(sum(contribs))]

        t = tabulate.tabulate(table, headers, tablefmt="plain", numalign="right", floatfmt=".3f")
        txt.line(t)
        return large_features, small_features

    def _description(self, large_features, small_features):
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

    def text(self, selected_features=None):
        self.txt = Report.RichTextBuilder()
        txt = list()
        tab = " " * 8
        self._header()
        # TODO implement
        # txt.append('Anomalous pattern cardinality to discard: ' + str(self.apc if self.apc is not None else 'N/A'))
        self._characteristics()
        # self._description()
        txt.append('<b>All features involved:</b>')
        for feature in self.norm_features:
            if not feature.is_nominal:
                txt.append("\t {} mean = {:10.3}; std = {:10.3};".format(feature.name, feature.series.mean(),
                                                                         feature.series.std()))
            else:
                txt.append("\t {} mean = Nominal; std = Nominal;".format(feature.name, feature.series.mean(),
                                                                         feature.series.std()))
        included = set()
        for feature in self.norm_features:
            include = feature in selected_features or selected_features is None
            if feature.is_nominal and include and feature.parent not in included:
                self.txt.line()
                self.txt.line("Nominal feature:{}".format(feature.parent.name), bold=True)
                self._nominal_feature_table(feature, "Absolute", Report.absolute_fun)
                f_table, N, margin_row, margin_col = self._nominal_feature_table(feature, "Frequency",
                                                                                 Report.frequency_fun)
                self._nominal_feature_table(feature,
                                            "Quetelet, relative change of probability of category, given a cluster",
                                            Report.quetelet_fun, suppress_marginal=True)
                self._chi_sq(f_table, N, margin_row, margin_col)
                included.add(feature.parent)
        self._contribution_feature_cluster(selected_features)
        self._contribution_feature_cluster(selected_features, relative=True)
        return self.txt.build()

    @staticmethod
    def frequency_fun(value, margin_row, margin_col, N):
        return value / N

    @staticmethod
    def absolute_fun(value, margin_row, margin_col, N):
        return value

    @staticmethod
    def quetelet_fun(value, margin_row, margin_col, N):
        return (value * N) / (margin_row * margin_col) - 1

    def _nominal_feature_table(self, feature, title, fun, suppress_marginal=False):
        txt = self.txt
        txt.line(title, tab=1)
        unique_values = list(feature.unique_values)
        headers = [Report.TAB + "Cluster #"] + unique_values + ["Total"]
        table = []
        for index, cluster in enumerate(self._cs.clusters):
            row = ["{}{}".format(Report.TAB, str(index + 1))]
            for u_value in unique_values:
                row += [int(sum(feature.parent.series[np.array(cluster.points_indices)] == u_value))]
            row += [sum(row[1:])]
            table += [row]
        total_row = [Report.TAB + "Total"]
        for u_value in unique_values:
            total_row += [int(sum(feature.parent.series == u_value))]
        total_row += [len(feature.parent.series)]
        table += [total_row]
        N = table[-1][-1]
        for row in range(0, len(table)):
            for col in range(1, len(table[0])):
                value = table[row][col]
                margin_row = table[-1][col]
                margin_col = table[row][-1]
                table[row][col] = fun(value, margin_row, margin_col, N)
        if suppress_marginal:
            table = [row[:-1] for row in table[:-1]]
            table += [['']]  # to force left align in first column
        t = tabulate.tabulate(table, headers, tablefmt="plain", numalign="right", floatfmt=".3f")
        # t = t[:t.rfind("\n")]
        txt.line(t)
        txt.line()
        margin_col = [x[-1] for x in table[:-1]]
        margin_row = table[-1][1:-1]
        return [x[1:-1] for x in table[:-1]], N, margin_row, margin_col

    def _chi_sq(self, f_table, N, margin_row, margin_col):
        chi = 0
        for row in range(0, len(f_table)):
            for col in range(0, len(f_table[0])):
                delta = margin_col[row] * margin_row[col]
                chi += (f_table[row][col] - delta) ** 2 / delta
        txt = self.txt
        from scipy.stats import chi2
        df = len(f_table) * len(f_table[0]) - 1
        N_df = chi2.ppf(0.05, df)
        txt.line("Chi square:{}".format(chi), bold=True, tab=1)
        txt.line("Phi square:{}".format(chi * N), bold=True, tab=1)
        if chi > N_df:
            txt.line(
                "Since chi2 = {:.3} is greater then the critical value = {:.3}, the hypothesis that the feature and clustering"
                "are statistically independent is rejected (confidence: 95%)".format(chi, N_df), tab=1)
        else:
            txt.line(
                "Since chi2 = {:.3} is less then the critical value = {:.3}, the hypothesis that the feature and clustering"
                "are statistically independent is accepted (confidence: 95%)".format(chi, N_df), tab=1)

    def _contribution_feature_cluster(self, features, relative=False):
        txt = self.txt
        txt.line()
        txt.line("Contribution of feature/cluster pair, %:", bold=True)
        if relative:
            txt.line("Relative (by normalized data)")
        else:
            txt.line("(by normalized data)")
        data = self._cs.data
        data_scatter = np.sum(data ** 2)
        headers = [Report.TAB + "Cluster #"] + [f.name for f in features]
        table = []
        for index, cluster in enumerate(self._cs.clusters):
            row = ["{}{}".format(Report.TAB, index + 1)]
            for feature in features:
                centroid = cluster.centroid
                power = cluster.power
                coordinate_index = self.norm_features.index(feature)
                coordinate = centroid[coordinate_index]
                value = 100 * (power * coordinate ** 2) / data_scatter
                if relative:
                    value /= np.sum(centroid**2)
                row += [value]
            table += [row]
        table += [[" "]]
        t = tabulate.tabulate(table, headers, tablefmt="plain", numalign="right", floatfmt=".3f")
        txt.line(t)

