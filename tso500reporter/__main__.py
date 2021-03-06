"""
Produces MSI and TMB reports given output files from the TSO500 local app
"""
import argparse
import os

import pandas as pd

from . import parser, plotter, reporter
from .constants import TMB_FIELDS, MSI_FIELDS

HTML_TEMPLATE_DIR = f"{os.path.dirname(__file__)}/templates"


def parse_arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument(
            "-d", "--variant-data", nargs="+", required=True,
            help="filepaths to <SAMPLE>_*CombinedVariantOutput.tsv files"
    )
    parser.add_argument(
            "-s", "--samplesheet", required=True,
            help="samplesheet"
    )
    parser.add_argument(
            "-o", "--output", default="report",
            help="directory to store report"
    )
    parser.add_argument(
            "-p", "--pdf", action="store_true", default=False,
            help="include PDF report"
    )

    args = parser.parse_args()

    return args

def main(variant_data, samplesheet, output="report", pdf=True):
    variant_df = parser.parse_variant_stats_data(*variant_data)

    # filter RNA samples
    samplesheet = parser.SampleSheet(samplesheet)
    samplesheet_df = pd.DataFrame(samplesheet.data)
    variant_df = pd.merge(
            variant_df,
            samplesheet_df,
            how="left",
            left_on="Pair ID",
            right_on="Pair_ID")
    variant_df = variant_df.loc[lambda df: df["Sample_Type"] != "RNA", :]

    # make output file
    os.makedirs(f"{output}/img")

    # plot and save TMB data
    tmb_fig = plotter.generate_plot(
            dataset=variant_df,
            x_column="DNA Sample ID",
            y_columns=TMB_FIELDS,
            fwidth=20,
            fheight=5)
    tmb_fig.savefig(f"{output}/img/tmb.png", bbox_inches="tight")

    # plot and save MSI data
    msi_fig = plotter.generate_plot(
            dataset=variant_df,
            x_column="DNA Sample ID",
            y_columns=MSI_FIELDS,
            fwidth=20,
            fheight=5)
    msi_fig.savefig(f"{output}/img/msi.png", bbox_inches="tight")

    # Write HTML report
    # need sequencing run header from one of the CVO files
    cvo = parser.CombinedVariantOutput(variant_data[0])
    run_name = cvo.sequencing_run_details["Run Name"]
    reporter.write_html(
            variant_df,
            embed=True,
            run_name=run_name,
            report_dir=output,
            template_dir=HTML_TEMPLATE_DIR)

    # Optionally write PDF report
    if pdf:
        reporter.write_pdf(output)

if __name__ == "__main__":

    args = parse_arguments()
    main(args.variant_data, args.samplesheet, args.output, args.pdf)
