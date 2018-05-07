import tabulate
import re

tabulate._invisible_codes = re.compile(r"\x1b\[\d+[;\d]*m|\x1b\[\d*\;\d*\;\d*m|<.*>")

tabulate_old = tabulate.tabulate
_visible_width_old = tabulate._visible_width
_strip_invisible_old = tabulate._strip_invisible

TAB = "<tab>"


def _strip_invisible(s):
    "Remove invisible ANSI color codes."
    try:
        s = re.sub(TAB, ' ' * 4, s)
        s = re.sub(r'<.*?>', '', s)
        s = re.sub('&nbsp;', ' ', s)
    except:
        pass
    return _strip_invisible_old(s)


tabulate._strip_invisible = _strip_invisible


def _visible_width(s):
    try:
        s = re.sub(TAB, ' ' * 4, s)
        s = re.sub(r'<.*?>', '', s)
        s = re.sub('&nbsp;', ' ', s)
    except:
        pass
    return _visible_width_old(s)


tabulate._visible_width = _visible_width


def tabulate(*args, **kwargs):
    res = tabulate_old(*args, **kwargs)
    # res = res.replace("\n", "<br>")
    return res


tabulate.tabulate = tabulate


class ReportHTMLPrinter:
    class Table:
        def __init__(self, header):
            self.table = []
            self.header = header

        def add_row(self, row):
            self.table += [row]

        def _sum_col(self, col):
            s = 0
            for row in range(0, len(self.table)):
                s += self.table[row][col]
            return s

        def to_lines(self, add_total=False):
            fmt = "fancy_grid"
            fmt = "plain"
            if add_total:
                self.add_row(["Total"] + [self._sum_col(c) for c in range(1, len(self.header))])
            t = tabulate.tabulate(self.table, self.header, tablefmt=fmt, numalign="right", floatfmt=".3f")
            return t.split("\n")

    def __init__(self, result, report, norm_data_df, raw_data_df=None, ari_series=None, calculate_sw=False,
                 threshold=0.30, font_size=14):
        self.result = result
        self.report = report
        self.ari_series = ari_series
        self.calculate_sw = calculate_sw
        self.text = ""
        self.norm_data_df = norm_data_df
        self.raw_data_df = raw_data_df
        self.threshold = threshold
        self.font_size = font_size

    def line(self, line="", tab=0, bold=False):
        if bold:
            self.text += "<b>" + line + "</b>" + "\n"
        else:
            self.text += line + "\n"

    def print_header(self):
        self.line('Clustering resulted in {} clusters'.format(self.report.clusters_number), bold=True)
        self.line()
        self.line('Algorithm used: {}({:.3} s);'.format(self.result.algorithm, self.result.algorithm.time), bold=True)

    def print_clustering_quality(self):
        if self.ari_series is not None:
            ari = self.report.ari(self.ari_series)
            self.line('Adjusted Rand Index (ARI) obtained: {:5.3f};'.format(ari))
        if self.calculate_sw:
            self.line('Silhouette Width (SW) obtained: {:5.3f};'.format(self.sw))

    def print_normalization(self):
        norm = self.result.normalization
        self.line('Normalization:')
        self.line(TAB + "Enabled: {}".format(norm.enabled), tab=1)
        if norm.enabled:
            self.line(TAB + "Center:  {}".format(norm.center), tab=1)
            self.line(TAB + "Spread:  {}".format(norm.spread), tab=1)

    def print_total(self, table, df):
        clusters = self.report.clusters
        table.add_row([TAB + "Total ({} entities)".format(sum(c.power for c in clusters))])
        table.add_row([2 * TAB + "Grand mean:"] + list(self.report.centroid(df)))
        table.add_row([2 * TAB + "Contribution, %:"] + [self.report.contribution(df)])

    def print_info(self, cluster, table, df, r_diff=False):
        table.add_row([TAB + "Cluster #{} ({} entities)".format(cluster.symbol, cluster.power)])
        table.add_row([2 * TAB + "Center:"] + list(cluster.centroid(df)))
        diff = cluster.centroid(df) - self.report.centroid(df)
        table.add_row([2 * TAB + "Difference:"] + list(diff))
        if r_diff:
            r_diff = 100 * diff / self.report.centroid(df)

            def color(elem):
                if float(elem) > 100 * self.threshold:
                    return '<font_color="{}">{}</font>'.format("red", elem)
                if -float(elem) > 100 * self.threshold:
                    return '<font_color="{}">{}</font>'.format("blue", elem)
                return elem

            r_diff_list = [color(rd) for rd in list(r_diff)]
            table.add_row([2 * TAB + "Difference, %:"] + r_diff_list)
        table.add_row([2 * TAB + "Contribution, %:"] + [cluster.contribution(df)])

    def print_clusters_info(self, type):
        df = self.raw_data_df if type == "raw" else self.norm_data_df
        r_diff = type == "raw"
        table = ReportHTMLPrinter.Table([self.title(type)] + list(df.columns))
        self.print_total(table, df)
        for cluster in self.report.clusters:
            self.print_info(cluster, table, df, r_diff)
        for l in table.to_lines():
            self.line(l)

    def title(self, type):
        if type == "norm":
            return "I. Normalized data"
        if type == "raw":
            return "II. Raw data"

    def print_description(self, cluster, df):
        self.line(TAB + "Cluster #{} ({} entities)".format(cluster.symbol, cluster.power))
        larger = cluster.large(df, self.threshold)
        if len(larger) > 0:
            self.line(2 * TAB + "larger:" + ','.join(larger))
        smaller = cluster.small(df, self.threshold)
        if len(smaller) > 0:
            self.line(2 * TAB + "smaller:" + ','.join(smaller))
        if len(smaller) == 0 and len(larger) == 0:
            self.line(2 * TAB + "nothing special")

    def print_clusters_description(self):
        df = self.raw_data_df
        self.line("Clusters description - raw data: (features significantly ({}) larger/smaller than average)".format(
            100 * self.threshold), bold=True)
        for cluster in self.report.clusters:
            self.print_description(cluster, df)

    def print_contrib_to_ds(self):
        self.line("Contribution to data scatter by features, %:", bold=True)
        self.line("(at normalized data)")
        df = self.norm_data_df
        table = ReportHTMLPrinter.Table([TAB + "Cluster #"] + list(df.columns)+["Total"])
        for cluster in self.report.clusters:
            cbf = cluster.contribution_by_features(df)
            table.add_row([1 * TAB + str(cluster.symbol)] + list(cbf) + [cbf.sum()])
        for l in table.to_lines(add_total=True):
            self.line(l)

    def print_feature_contrib(self):
        df = self.norm_data_df
        fc = self.report.feature_contribution(df) * 100
        table = ReportHTMLPrinter.Table(["Feature:"] + list(df.columns))
        table.add_row(["Contribution, %"] + list(fc))
        for l in table.to_lines():
            self.line(l)

    def print_relative_contrib_to_ds(self):
        self.line("Relative contribution to feature, %:", bold=True)
        self.line("(at normalized data)")
        df = self.norm_data_df
        fc = self.report.feature_contribution(df)
        table = ReportHTMLPrinter.Table(["Cluster #"] + list(df.columns))
        for cluster in self.report.clusters:
            cbf = cluster.contribution_by_features(df)
            cbfr = cbf / fc
            table.add_row([str(cluster.symbol)] + list(cbfr))
        for l in table.to_lines(add_total=True):
            self.line(TAB + l)

    def post_process(self):
        span_open = '<span style=" font-size:{fs}pt;font-family:monospace" >'.format(fs=self.font_size)
        span_close = '<span>'
        self.text = self.text.replace(TAB, "&nbsp;" * 4)
        self.text = self.text.replace(" ", "&nbsp;")
        self.text = self.text.replace("\n", "<br>")
        self.text = self.text.replace("font_color", "font color")
        self.text = span_open + self.text + span_close

    def print(self):
        self.text = ""
        self.print_header()
        self.print_normalization()
        self.print_clustering_quality()
        self.line()

        self.line("Clusters characteristics:", bold=True)
        self.print_clusters_info("norm")
        self.line()

        if self.raw_data_df is not None:
            self.print_clusters_info("raw")
            self.line()
            self.print_clusters_description()
        self.line()

        self.print_contrib_to_ds()
        self.line()

        self.print_feature_contrib()
        self.line()

        self.print_relative_contrib_to_ds()
        self.post_process()
        return self.text
