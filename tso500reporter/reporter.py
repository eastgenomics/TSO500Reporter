"""
Handles reporting of plots and data to HTML and PDF
"""
import base64
from jinja2 import Environment, FileSystemLoader
import pandas as pd
from weasyprint import HTML

from .constants import TMB_FIELDS, MSI_FIELDS


def to_base64(png: str) -> str:
    """
    Encodes a PNG as a base64 encoded string, embedding
    it in the file.
    """

    with open(png, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    return f"data:image/png;base64,{encoded_string}"


def write_html(
        dataset: pd.DataFrame,
        run_name: str = None,
        embed = False,
        report_dir: str = "report",
        template_dir: str = "templates",
        html_template_name: str = "template.html",
        css_template_name: str = "styles.css") -> None:
    """
    Writes the dataset (as a table) and plots to a HTML.
    The function assumes the plots have already been
    generated and stored in PNG format.

    Args:
        dataset: the `pd.DataFrame` as produced
            by `parser.parse_variant_output_files()`
        report_dir: directory to store the reports
        template_dir: directory containing the HTML and CSS templates
        template_name: the filename of the HTML template to use

    Returns:
        None
    """
    tmb_data = dataset[["DNA Sample ID"] + TMB_FIELDS]
    msi_data = dataset[["DNA Sample ID"] + MSI_FIELDS]

    # Create a template Environment
    env = Environment(loader=FileSystemLoader(template_dir))

    # Load the template from the Environment
    template = env.get_template(html_template_name)

    # handle PNG embedding
    if embed:
        tmb_image = to_base64(f"{report_dir}/img/tmb.png")
        msi_image = to_base64(f"{report_dir}/img/msi.png")
    else:
        tmb_image = f"{report_dir}/img/tmb.png"
        msi_image = f"{report_dir}/img/msi.png"

    # Render the template with variables
    html = template.render(page_title_text='TSO500 TMB & MSI',
                           run_name=run_name,
                           tmb_plot_path=tmb_image,
                           tmb_data=tmb_data,
                           msi_plot_path=msi_image,
                           msi_data=msi_data,
                           template_dir=template_dir,
                           css_template=css_template_name)

    # 4. Write output
    with open(f"{report_dir}/report.html", "w") as f:
        f.write(html)


def write_pdf(report_dir: str) -> None:
    """
    Produces a PDF report using the HTML report
    (produced by `write_html`) as template.

    Args:
        report_dir: the directory containing the reports
        css_filepath: the path to the CSS template

    Returns:
        None
    """
    HTML(f"{report_dir}/report.html").write_pdf(target=f"{report_dir}/report.pdf")
