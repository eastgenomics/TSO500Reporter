# TSO500Reporter

A library for parsing `*CombinedVariantOutput.tsv` files, visualising the data, and producing HTML or PDF reports. Currently, reports support only microsatellite instability (MSI) and tumour mutational burden (TMB) metrics.

## Installation

This package is installable. Run the following after cloning the repository locally:

```shell
cd TSO500Reporter
pip3 install .
```

## Usage

### Reporting

After installation, run the following command to produce the report:

```shell
python3 -m tso500reporter --variant-data /path/to/*CombinedVariantOutput.tsv --samplesheet /path/to/SampleSheet.csv --output /path/to/output --pdf 
```

This will write an HTML and PDF report to the specified output directory containing Tumour Mutational Burden (TMB) and Microsatellite Instability (MSI) metrics.
Please refer to the following links for examples of the [HTML][html-report-link] and [PDF][pdf-report-link] reports.

#### Usage

```shell
usage: __main__.py [-h] -d VARIANT_DATA [VARIANT_DATA ...] -s SAMPLESHEET [-f] [-o OUTPUT] [-p]

optional arguments:
  -h, --help            show this help message and exit
  -d VARIANT_DATA [VARIANT_DATA ...], --variant-data VARIANT_DATA [VARIANT_DATA ...]
                        filepaths to <SAMPLE>_*CombinedVariantOutput.tsv files
  -s SAMPLESHEET, --samplesheet SAMPLESHEET
                        samplesheet
  -o OUTPUT, --output OUTPUT
                        directory to store report
  -p, --pdf             include PDF report
```

### In scripts

TSO500Reporter also features an API for interaction with the data in each section of the TSO500 input and output files. This allows extraction of data not featured in the output report when the module is executed directly. The classes facilitate interaction with individual sections as lists or dicts of data, or with the entire dataset in JSON format, allowing further data analysis.

#### SampleSheet data

For example, we can import the samplesheet and gain access to the **[Header]** section, or the samplesheet **[Data]** section itself (note: staff names and sample IDs have been redacted):

```python
>>> from tso500reporter.parser import SampleSheet
>>> samplesheet_path = "/path/to/SampleSheet.csv"
>>> samplesheet = SampleSheet(samplesheet_path)
>>> samplesheet.header

{'IEMFileVersion': '4',
 'Investigator': 'XXXXX XXXXX',
 'Experiment': 'TSOVal16',
 'Date': 'Fri Oct 15 10:14:47 GMT 2021',
 'Workflow': 'GenerateFASTQ',
 'Application': 'NovaSeq FASTQ Only',
 'Assay': 'TSO500 HT',
 'Description': 'TSOVal16',
 'Chemistry': 'Default'}

>>> samplesheet.data[0]

{'Sample_ID': 'XXXXXXXXX-X-XXXXXX-DNA-egg6',
 'Sample_Name': 'XXXXXXXXX-X-XXXXXX-DNA-egg6',
 'Sample_Plate': 'XX-XXXX',
 'Sample_Well': 'XX',
 'Index_ID': 'UDP0065',
 'index': 'TAATGTGTCT',
 'index2': 'TATGCCTTAC',
 'Sample_Type': 'DNA',
 'Pair_ID': 'XXXXXXXXX-X'}
```

#### CombinedVariantOutput data

We can also interact directly with  _*CombinedVariantOutput.tsv_ files. Here, we display the **[Analysis Details]** section, and a row from the **[Small Variants]** section:

```python
>>> from tso500reporter.parser import CombinedVariantOutput

>>> cvo_filepath = "/path/to/SAMPLE_CombinedVariantOutput.tsv"

>>> cvo_data = CombinedVariantOutput(cvo_filepath)

>>> cvo_data.analysis_details

{'Pair ID': 'XXXXXXXXX-X',
 'DNA Sample ID': 'XXXXXXXXX-X-XXXXXX-DNA-egg6',
 'RNA Sample ID': 'NA',
 'Output Date': '2021-10-19',
 'Output Time': '05:07:44',
 'Module Version': 'NA',
 'Pipeline Version': 'ruo-2.2.0.12'}

>>> cvo_data.small_variants[0]

{'Gene': 'TNFRSF14',
 'Chromosome': 'chr1',
 'Genomic Position': '2488153',
 'Reference Call': 'A',
 'Alternative Call': 'G',
 'Allele Frequency': '0.4990',
 'Depth': '477',
 'P-Dot Notation': 'NP_003811.2:p.(Lys17Arg)',
 'C-Dot Notation': 'NM_003820.3:c.50A>G',
 'Consequence(s)': 'missense_variant',
 'Affected Exon(s)': '1/8'}
```

Alternatively, we can access all of the data at once by accessing the `json` attribute:

```python
>>> cvo_data.json.keys()

dict_keys(['Analysis Details', 'Sequencing Run Details', 'TMB', 'MSI', 'Gene Amplifications', 'Splice Variants', 'Fusions', 'Small Variants'])
```

[html-report-link]: https://htmlpreview.github.io/?https://github.com/eastgenomics/TSO500Reporter/blob/master/examples/report.html
[pdf-report-link]: examples/report.pdf
