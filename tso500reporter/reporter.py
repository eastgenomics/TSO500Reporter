from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

from constants import TMB_FIELDS, MSI_FIELDS

css = CSS(string='''
    @page {size: A4, margin=1cm;}
    th, td {border: 1px solid black;}
    ''')

def write_html(dataset, report_dir="report", template_dir="templates", template_name="template.html"):
    """
    docs here
    """
    tmb_data = dataset[["Pair ID"] + TMB_FIELDS]
    msi_data = dataset[["Pair ID"] + MSI_FIELDS]

    # Create a template Environment
    env = Environment(loader=FileSystemLoader(template_dir))

    # Load the template from the Environment
    template = env.get_template(template_name)

    # Render the template with variables
    html = template.render(page_title_text='TSO500 TMB & MSI',
                           tmb_plot_path=f"img/tmb.png",
                           tmb_data=tmb_data,
                           msi_plot_path=f"img/msi.png",
                           msi_data=msi_data,
                           template_dir=template_dir)

    # 4. Write output
    with open(f"{report_dir}/report.html", "w") as f:
        f.write(html)

def write_pdf(report_dir, css=css):
    """
    writes PDF from html
    """
    HTML(f"{report_dir}/report.html").write_pdf(f"{report_dir}/report.pdf", stylesheets=[css])
