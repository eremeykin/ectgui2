from report.report_html_printer import ReportHTMLPrinter
from report.report_html_printer import TAB
import re


class ReportPlainPrinter(ReportHTMLPrinter):
    def __init__(self, result, report, norm_data_df, raw_data_df=None, ari_series=None, calculate_sw=False,
                 threshold=0.30, font_size=14):
        super(ReportPlainPrinter, self).__init__(result, report, norm_data_df, raw_data_df, ari_series, calculate_sw,
                                                 threshold, font_size)

    def post_process(self):
        self.text = self.text.replace(TAB, " " * 4)
        self.text = re.sub(r"<.*?>", "", self.text)
