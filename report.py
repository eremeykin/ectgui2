from progress_gialog.progress_dialog import ProgressDialog
import re

import numpy as np
import tabulate
from PyQt5.QtWidgets import *

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
            text = "\n".join(["{tab}{txt}".format(tab=Report.TAB * tab, txt=text) for line in text.split('\n')])
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
            formated_res.append('<span style=" font-size:{fs}pt;font-family:monospace" >'.format(fs=self.font_size))
            formated_res.extend(res)
            formated_res.append('<img src="svd.png" alt="SVD">')
            formated_res.append('</span>')
            return '\n<br>'.join(formated_res)

    def __init__(self, parent, cluster_structure, algorithm, normalization, norm_features, time, sw=None):
        self.parent = parent
        self._cs = cluster_structure
        self.algorithm = algorithm
        self.normalization = normalization
        self.norm_features = norm_features
        self.r_norm = normalization.reverse(norm_features)
        self.txt = Report.RichTextBuilder()
        self.time = time
        self.calculate_sw = False
        self.sw = sw

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
        txt.line('Intelligent clustering resulted in {} clusters'.format(self._cs.clusters_number), bold=True)
        txt.line()
        txt.line('Algorithm used: {}({:.3} s);'.format(self.algorithm, self.time))
        ari_feature = None
        for f in self.parent.all_features():
            if 'A' in f.markers:
                ari_feature = f
                break

        if ari_feature is not None:
            from sklearn.metrics.cluster import adjusted_rand_score as ari
            series = ari_feature.series
            for i, uv in enumerate(series.unique()):
                series[series == uv] = i
            a = ari(series.as_matrix(), self._cs.current_labels())
            txt.line('Adjusted Rand Index (ARI) obtained: {:5.3f};'.format(a))
        if self.calculate_sw:
            self._calculate_sw()
            # while self.sw is None:
            #     pass
            txt.line('Silhouette Width (SW) obtained: {:5.3f};'.format(self.sw))
        txt.line('Normalization:')
        txt.line("Enabled: {}".format(self.normalization.enabled), tab=1)
        if self.normalization.enabled:
            txt.line("Center:  {}".format(self.normalization.center), tab=1)
            txt.line("Spread:  {}".format(self.normalization.spread), tab=1)

    def _calculate_sw(self):
        from clustering.agglomerative.utils.choose_p import ChooseP
        SW = ChooseP.AvgSilhouetteWidthCriterion()

        def do_it():
            try:
                self.sw = SW(self._cs)
            except:
                self.sw = "an error occurred"

        progress = "Calculating SW"
        p_dialog = ProgressDialog(self.parent, progress, do_it, autofininsh=False)
        p_dialog.run(wait=True)

    def _characteristics(self):
        txt = self.txt
        txt.line('Clusters characteristics:', bold=True)
        self._abstr_characteristics("I. Normalized data", self._cs.data, lambda c: c.centroid)
        l, s = self._abstr_characteristics("II. Raw data",
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
        large_features = []
        small_features = []
        # pre calculate contributions
        contribs = []
        for cluster in self._cs.clusters:
            centroid = centroid_fun(cluster)
            contribution = 100 * cluster.power * (centroid @ centroid[None].T) / (np.sum(data * data))
            contribs.append(contribution)
        table += [["{}Total ({} entities):".format(tab, sum([c.power for c in self._cs.clusters]))]]
        table += [["{}{}".format(tab * 2, "Grand mean:")] + [x for x in g_mean]]
        table += [["{}{}".format(tab * 2, "Contribution, %:")] + list(sum(contribs))]

        for index, cluster in enumerate(self._cs.clusters):
            table += [["{}Cluster #{} ({} entities):".format(tab, index + 1, cluster.power)]]
            centroid = centroid_fun(cluster)
            table += [["{}Center".format(tab * 2)] + [x for x in centroid]]
            # diff
            diff = centroid - g_mean
            table += [["{}Difference:".format(tab * 2)] + [x for x in diff]]
            if add_diff_relative:
                diff_relative = 100 * diff / g_mean
                colored = self._color_array([x for x in diff_relative],
                                            [lambda elem: float(elem) > 100 * Report.THRESHOLD,
                                             lambda elem: -float(elem) > 100 * Report.THRESHOLD],
                                            ['red', 'blue'])
                table += [["{}Difference, %:".format(tab * 2)] + colored]
                large_features.append(
                    [feature for i, feature in enumerate(self.norm_features) if diff_relative[i] > Report.THRESHOLD])
                small_features.append(
                    [feature for i, feature in enumerate(self.norm_features) if -diff_relative[i] > Report.THRESHOLD])
                # np.array([self.norm_features])[diff_relative > Report.THRESHOLD])
                # small_features.append(np.array([self.norm_features])[-diff_relative > Report.THRESHOLD])
            # cluster contribution
            table += [["{}Contribution, %:".format(tab * 2), contribs[index]]]
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

    def text(self, selected_features=None, plain=False):
        msg = QMessageBox()
        msg.setWindowTitle("Calculate SW?")
        msg.setText("Would you like to calculate SW value? (time consuming)")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_res = msg.exec_()
        self.calculate_sw = msg_res == QMessageBox.Yes
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
                self._nominal_feature_table(feature, "Frequency", Report.frequency_fun)
                f_table, N, margin_row, margin_col = self._nominal_feature_table(feature, "Relative frequency",
                                                                                 Report.relative_frequency_fun)
                self._nominal_feature_table(feature, "Quetelet index: relative change of the category probability,"
                                                     " given a cluster",
                                            Report.quetelet_fun, suppress_marginal=True, fmt=".1f")
                self._chi_sq(f_table, N, margin_row, margin_col)
                included.add(feature.parent)
        self._contribution_feature_cluster(selected_features)
        self._contribution_feature_cluster(selected_features, relative=True, suppress_marginal_col=True)
        result = self.txt.build()
        if plain:
            import re
            result = result.replace("<br>", "\n")
            result = re.sub("<.*?>", "", result)
            return result.replace("&nbsp;", " ")
        return result

    @staticmethod
    def relative_frequency_fun(value, margin_row, margin_col, N):
        return value / N

    @staticmethod
    def frequency_fun(value, margin_row, margin_col, N):
        return value

    @staticmethod
    def quetelet_fun(value, margin_row, margin_col, N):
        return ((value * N) / (margin_row * margin_col) - 1) * 100

    def _nominal_feature_table(self, feature, title, fun, suppress_marginal=False, fmt=".3f"):
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
                # table[row][col] = self._color_array(table[row],
                #                                     [lambda elem: float(elem.replace('&nbsp;', '')) > 50,
                #                                      lambda elem: -float(elem.replace('&nbsp;', '')) < -50],
                #                                     ['red', 'blue'])
        if suppress_marginal:
            table = [row[:-1] for row in table[:-1]]
            table += [['']]  # to force left align in first column
        t = tabulate.tabulate(table, headers, tablefmt="plain", numalign="right", floatfmt=fmt)
        # t = t[:t.rfind("\n")]
        txt.line(t)
        txt.line()
        margin_col = [x[-1] for x in table[:-1]]
        margin_row = table[-1][1:-1]
        return [x[1:-1] for x in table[:-1]], N, margin_row, margin_col

    def _chi_sq(self, f_table, N, margin_row, margin_col):
        phi2 = 0
        for row in range(0, len(f_table)):
            for col in range(0, len(f_table[0])):
                delta = margin_col[row] * margin_row[col]
                phi2 += (f_table[row][col] - delta) ** 2 / delta
        txt = self.txt
        from scipy.stats import chi2
        df = len(f_table) * len(f_table[0]) - 1
        N_df = chi2.ppf(1 - 0.05, df)
        chi2 = phi2 * N
        txt.line("Phi square:{}".format(phi2), bold=True, tab=1)
        txt.line("Chi square:{}".format(chi2), bold=True, tab=1)
        if chi2 > N_df:
            # rejected
            txt.line(
                "Since chi2 = {:.5} is greater then the critical value = {:.3} (for df = {}), the hypothesis that the ".format(
                    chi2, N_df, df), tab=1)
            txt.line("feature and clustering"
                     " are statistically independent is rejected (confidence: 95%)", tab=1)
            txt.line("In fact, the feature and clustering are related so that knowledge", tab=1)
            txt.line("of cluster raises the chances of feature categories by {:5.1f}%.".format(phi2 * 100), tab=1)
        else:
            # accepted
            txt.line(
                "Since chi2 = {:.5} is less then the critical value = {:.3} (for df = {}), the hypothesis that the ".format(
                    chi2, N_df, df), tab=1)
            txt.line("feature and clustering are statistically independent is accepted (confidence: 95%)", tab=1)

    def _contribution_feature_cluster(self, features, relative=False, suppress_marginal_col=False):
        txt = self.txt
        txt.line()
        data = self._cs.data
        data2 = data ** 2
        data_scatter = np.sum(data2)
        feature_contribution = np.sum(data2, axis=0) / data_scatter
        if relative:
            txt.line("Feature contribution, %:", bold=True)
            headers = [f.name for f in features] + ["Total"]
            table = [list(feature_contribution * 100)]
            t = tabulate.tabulate(table, headers, tablefmt="plain", numalign="right", floatfmt=".3f")
            for line in t.split("<br>"):
                txt.line(line, tab=2)
            txt.line()
            txt.line("Relative contribution to feature, %:", bold=True)
        else:
            txt.line("Contribution to data scatter, %:", bold=True)
        if self.normalization.enabled:
            txt.line("(at normalized data)")
        else:
            txt.line("(normalization is disabled)")
        headers = [Report.TAB + "Cluster #"] + [f.name for f in features] + ["Total"]
        table = []
        for index, cluster in enumerate(self._cs.clusters):
            row = ["{}{}".format(Report.TAB, index + 1)]
            total_row = 0
            for f_index, feature in enumerate(features):
                centroid = cluster.centroid
                power = cluster.power
                coordinate_index = self.norm_features.index(feature)
                coordinate = centroid[coordinate_index]
                value = 100 * (power * coordinate ** 2) / data_scatter
                if relative:
                    value /= feature_contribution[f_index]
                    # np.sum(centroid ** 2)
                total_row += value
                row += [value]
            row += [total_row]
            table += [row]

        total_row = [Report.TAB + "Total"]
        for col in range(1, len(table[0])):
            col_sum = 0
            for row in range(0, len(table)):
                col_sum += table[row][col]
            total_row += [col_sum]
        table += [total_row]
        if suppress_marginal_col:
            table = [row[:-1] for row in table]
        table += [[" "]]
        t = tabulate.tabulate(table, headers, tablefmt="plain", numalign="right", floatfmt=".3f")
        txt.line(t)
