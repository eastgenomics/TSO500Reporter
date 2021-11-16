#!/bin/bash
# TSO500Reporter DNANexus app

set -exo pipefail

main() {

    echo "Fetching inputs..."

    # Download samplesheet
    dx download "$samplesheet"
    
    # Download CombinedVariantOutput.tsv files
    for cvo_file in "${combined_variant_output_files[@]}"
    do
        dx download "$cvo_file"
    done

    # Install python3
    echo "Installing Python3..."
    cd ~
    tar -xvzf Python-3.10.0.tar.xz
    cd Python-3.*
    ./configure
    make install

    # Install python packages
    echo "Installing Python packages..."

    cd ~

    ## Install wheel first...
    pip3 install packages/wheel/wheel-0.37.0-py2.py3-none-any.whl

    ## ...then install dependencies
    pip3 install packages/*.whl

    cd ~

    # Generate report
    echo "Running app..."
    time python3 -m tso500reporter --variant-data *CombinedVariantOutput.tsv --samplesheet *.csv --output $output --pdf

    # Upload report
    echo "Completed. Uploading files..."

    ## Fetch output report files
    html_report=$(find . report.html)
    pdf_report=$(find . report.pdf)

    ## Upload files to DNANexus
    html_report_id=$(dx upload $html_report --brief)
    pdf_report_id=$(dx upload $pdf_report --brief)

    ## Add workflow-output tag from outputSpec to files
    dx-jobutil-add-output report_html "$html_report_id" --class=file
    dx-jobutil-add-output report_pdf "$pdf_report_id" --class=file
}
