import argparse
import os

import pandas as pd
import matplotlib.pyplot as plt

from . import parser
from . import plotter
from . import reporter
from .constants import TMB_FIELDS, MSI_FIELDS

HTML_TEMPLATE_DIR = f"{os.path.dirname(__file__)}/templates"

def parse_arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--data", help="combined variant output files", nargs="+", required=True)
    parser.add_argument("-s", "--samplesheet", help="samplesheet", required=True)
    parser.add_argument("-f", "--filter-rna", help="remove RNA samples from output", action="store_true", default=True)
    parser.add_argument("-o", "--output", help="directory to store report", default="report")
    parser.add_argument("-p", "--pdf", help="include PDF report", action="store_true", default=False)

    args = parser.parse_args()

    return args

if __name__ == "__main__":

    args = parse_arguments()

    variant_df = parser.parse_variant_stats_data(*args.data)

    # filter RNA samples
    if args.filter_rna:
        samplesheet = parser.read_samplesheet(args.samplesheet)
        samplesheet_df = pd.DataFrame(samplesheet["Data"])
        variant_df = pd.merge(variant_df, samplesheet_df, how="left", left_on="Pair ID", right_on="Pair_ID")
        variant_df = variant_df.loc[lambda df: df["Sample_Type"] != "RNA", :]

    os.makedirs(f"{args.output}/img")

    tmb_fig = plotter.generate_plot(dataset=variant_df, x_column="Pair ID", y_columns=TMB_FIELDS, fwidth=20, fheight=5)
    tmb_fig.savefig(f"{args.output}/img/tmb.png", bbox_inches="tight")

    msi_fig = plotter.generate_plot(dataset=variant_df, x_column="Pair ID", y_columns=MSI_FIELDS, fwidth=20, fheight=5)
    msi_fig.savefig(f"{args.output}/img/msi.png", bbox_inches="tight")

    reporter.write_html(variant_df, report_dir=args.output, template_dir=HTML_TEMPLATE_DIR)

    if args.pdf:
        reporter.write_pdf(args.output, css_file=f"{HTML_TEMPLATE_DIR}/styles.css")
