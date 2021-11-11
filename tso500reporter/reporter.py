"""
Handles reporting of plots and data to HTML and PDF
"""
import os

from jinja2 import Environment, FileSystemLoader
import pandas as pd
from weasyprint import HTML, CSS

from .constants import TMB_FIELDS, MSI_FIELDS

def write_html(dataset: pd.DataFrame, report_dir: str="report", template_dir:str ="templates", template_filename:str ="template.html") -> None:
    """
    Writes the dataset (as a table) and plots to a HTML. The function assumes the plots have already
    been generated and stored in PNG format.

    Args:
        dataset: the `pd.DataFrame` as produced by `parser.parse_variant_output_files`
        report_dir: directory to store the reports
        template_dir: directory containing the HTML and CSS templates
        template_name: the filename of the HTML template to use

    Returns:
        None
    """
    tmb_data = dataset[["Pair ID"] + TMB_FIELDS]
    msi_data = dataset[["Pair ID"] + MSI_FIELDS]

    # Create a template Environment
    env = Environment(loader=FileSystemLoader(template_dir))

    # Load the template from the Environment
    template = env.get_template(template_filename)

    # Render the template with variables
    html = template.render(page_title_text='TSO500 TMB & MSI',
                           tmb_plot_path="img/tmb.png",
                           tmb_data=tmb_data,
                           msi_plot_path="img/msi.png",
                           msi_data=msi_data,
                           template_dir=template_dir)

    # 4. Write output
    with open(f"{report_dir}/report.html", "w") as f:
        f.write(html)

def write_pdf(report_dir: str, css_filepath: str) -> None:
    """
    Produces a PDF report using the HTML report (produced by `write_html`) as template.

    Args:
        report_dir: the directory containing the reports
        css_filepath: the path to the CSS template

    Returns:
        None
    """
    HTML(f"{report_dir}/report.html").write_pdf(f"{report_dir}/report.pdf", stylesheets=[CSS(filename=css_file)])
