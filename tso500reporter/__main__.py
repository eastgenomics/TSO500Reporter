import argparse
import matplotlib.pyplot as plt
import os

from . import parser
from . import plotter
from . import reporter
from .constants import TMB_FIELDS, MSI_FIELDS

HTML_TEMPLATE_DIR = f"{os.path.dirname(__file__)}/templates"

def parse_arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--data", help="combined variant output files", nargs="+", required=True)
    parser.add_argument("-o", "--output", help="directory to store report", default="report")
    parser.add_argument("-p", "--pdf", help="include PDF report", action="store_true", default=False)

    args = parser.parse_args()

    return args

if __name__ == "__main__":

    args = parse_arguments()

    df = parser.parse_data(*args.data)

    os.makedirs(f"{args.output}/img")

    tmb_fig = plotter.generate_plot(dataset=df, x_column="Pair ID", y_columns=TMB_FIELDS, fwidth=20, fheight=5)
    tmb_fig.savefig(f"{args.output}/img/tmb.png", bbox_inches="tight")

    msi_fig = plotter.generate_plot(dataset=df, x_column="Pair ID", y_columns=MSI_FIELDS, fwidth=20, fheight=5)
    msi_fig.savefig(f"{args.output}/img/msi.png", bbox_inches="tight")

    reporter.write_html(df, report_dir=args.output, template_dir=HTML_TEMPLATE_DIR)

    if args.pdf:
        reporter.write_pdf(args.output, css_file=f"{HTML_TEMPLATE_DIR}/styles.css")
