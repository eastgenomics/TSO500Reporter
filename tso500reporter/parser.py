"""
Classes for parsing files used in, and produced by, Illumina's TSO500 app
"""
from collections import ChainMap
import re
from typing import Union, Dict, List, Any

import pandas as pd

from .constants import TMB_FIELDS, MSI_FIELDS

JSONType = Dict[Dict[str, Any], List[Dict[str, Any]]]

class IlluminaFile(object):
    """
    Class for handling the contents of files outputted by the TSO500 local app.

    This class should not be directly used - derived classes are available for
    different types of output (e.g. the samplesheet and combined variant output),
    which should be used to interact with those files instead.

    Attributes:
        filename: path to file
        json: contents of the file as a dict

    Refer to derived classes for examples of usage.
    """
    def __init__(self, filename: str=None, delim: str=None, skip: int=0, tabular_sections: List[str]=[], array_sections: List[str]=[]) -> None:
        """
        Inits IlluminaFile with filename, delimiter, the number of lines to skip (due to
        boilerplate lines at the top of some output files), and lists of sections to be 
        handled in specific ways by `IlluminaFile._read()`. I.e.:

            - `tabular sections` are handled as delimiter-separated data;
            - `array sections` are handled as simple lists of data

        Note that derived classes set many of these arguments as defaults,
        not to be set by the user.

        Args:
            filename: path to file
            delim: file delimiter (e.g. `","` `"\t"` etc.)
            skip: number of lines to skip over before parsing the file
            tabular_sections: List of sections where the data is formatted as
                delimiter-separated data
            array_sections: List of sections where the data is formatted as
                a simple list of entries
        """
        self.filename = filename
        self._tabular_sections = tabular_sections
        self._array_sections = array_sections
        self._delim = delim
        self._skip = skip
        self.json = None

    @property
    def json(self) -> JSONType:
        """
        Contents of file as a dict
        """
        return self._json

    @json.setter
    def json(self, val):
        if val is None:
            self._json = self._read()

    def _read(self) -> str: 
        """
        Reads the contents of the imported file into a dict
        """
        with open(self.filename, "r") as f:
            file_contents = {}

            ## some files have license/use info at the top. Skip these lines
            if self._skip > 0:
                [next(f) for i in range(self._skip)]

            for line in f:
                line = line.rstrip("\n")

                ## skip over lines entirely made of delimiters; these are section breaks
                if re.match(f"^{self._delim}+$", line):
                    continue

                ## handle section header
                elif line[0] == "[":
                    header = self._extract_header(line)

                    if header in self._tabular_sections:
                        ## section head followed by column names. Go to next line in
                        ## file here and extract column names. The rest of the 
                        ## lines can be handled like normal tabular data (CSV, TSV etc.) 
                        column_names = f.readline().rstrip().split(self._delim)
                        file_contents[header] = []
                        data_type = "tabular"
                    elif header in self._array_sections:
                        file_contents[header] = []
                        data_type = "array"
                    else:
                        file_contents[header] = {}
                        data_type = "record"

                ## handle section data
                else:
                    row = line.split(self._delim)
                    if data_type == "tabular":
                        if len(row) < len(column_names):
                            n_missing_values = len(column_names) - len(row)
                            row += ["NA" for i in range(n_missing_values)]
                        file_contents[header].append(dict(zip(column_names, row)))

                    elif data_type == "array":
                        value = row[0]
                        file_contents[header].append(value)

                    else:
                        ## i.e. data_type == "record"
                        ## Non-TSV formatted KV pairs can be dict'd normally
                        key = row[0]
                        value = row[1]
                        file_contents[header][key] = value

        return(file_contents) 

    def _extract_header(self, header_string: str) -> str:
        """
        Extracts the name of the section header as a string
        """
        return re.search('\[(.+)\]', header_string).group(1)

class CombinedVariantOutput(IlluminaFile):
    """
    Class for parsing `<SAMPLE>_CombinedVariantOutput.tsv` output files

    Longer class info...
    Longer class info...

    Attributes:
        filename: path to file
        analysis_details: Analysis metadata
        sequencing_run_details: Sequencing run metadata
        tmb: TMB (Tumour Mutational Burden) statistics
        msi: MSI (Microsatellite Instability) statistics
        gene_amplifications: Gene amplification statistics
        splice_variants: Splice variant statistics
        fusions: Gene fusion statistics
        small_variants: Small variant statistics
    """
    def __init__(self, filename: str) -> None:
        """
        Inits CombinedVariantOutput with filename

        Args: 
            filename: path to <SAMPLE>_CombinedVariantOutput.tsv file
        """
        super().__init__(filename=filename, delim="\t", tabular_sections=["Gene Amplifications", "Splice Variants", "Fusions", "Small Variants"], array_sections=[], skip=2)
        self.analysis_details = None
        self.sequencing_run_details = None
        self.tmb = None
        self.msi = None
        self.gene_amplifications = None
        self.splice_variants = None
        self.fusions = None
        self.small_variants = None

    @property
    def analysis_details(self) -> dict:
        """
        Returns analysis metadata
        """
        return self._analysis_details

    @analysis_details.setter
    def analysis_details(self, val):
        if val is None:
            self._analysis_details = self.json["Analysis Details"]

    @property
    def sequencing_run_details(self) -> dict:
        """
        Returns sequencing run metadata
        """
        return self._sequencing_run_details

    @sequencing_run_details.setter
    def sequencing_run_details(self, val):
        if val is None:
            self._sequencing_run_details = self.json["Sequencing Run Details"]

    @property
    def tmb(self) -> dict:
        """
        Returns Tumour Mutational Burden statistics
        """
        return self._tmb

    @tmb.setter
    def tmb(self, val):
        if val is None:
            self._tmb = self.json["TMB"]

    @property
    def msi(self) -> dict:
        """
        Returns Microsatellite Instability statistics
        """
        return self._msi

    @msi.setter
    def msi(self, val):
        if val is None:
            self._msi = self.json["MSI"]

    @property
    def gene_amplifications(self) -> List[dict]:
        """
        Returns gene amplification statistics
        """
        return self._gene_amplifications

    @gene_amplifications.setter
    def gene_amplifications(self, val):
        if val is None:
            self._gene_amplifications = self.json["Gene Amplifications"]

    @property
    def splice_variants(self) -> List[dict]:
        """
        Returns splice variant statistics
        """
        return self._splice_variants

    @splice_variants.setter
    def splice_variants(self, val):
        if val is None:
            self._splice_variants = self.json["Splice Variants"]

    @property
    def fusions(self) -> List[dict]:
        """
        Returns gene fusion statistics
        """
        return self._fusions

    @fusions.setter
    def fusions(self, val):
        if val is None:
            self._fusions = self.json["Fusions"]

    @property
    def small_variants(self) -> List[dict]:
        """
        Returns small variant statistics
        """
        return self._small_variants

    @small_variants.setter
    def small_variants(self, val):
        if val is None:
            self._small_variants = self.json["Small Variants"]


class SampleSheet(IlluminaFile):
    """
    Class for parsing TSO500-specific `*_SampleSheet.csv` files

    Longer class info...
    Longer class info...

    Attributes:
        filename: path to file
        header: samplesheet header (i.e. analysis metadata)
        reads: read lengths
        settings: various program-specific settings
        data: samplesheet data
    """
    def __init__(self, filename):
        super().__init__(filename, delim=",", tabular_sections=["Data"], array_sections=["Reads"], skip=0)
        self.header = None
        self.reads = None
        self.settings = None
        self.data = None

    @property
    def header(self) -> dict:
        """
        Returns samplesheet header
        """
        return self._header

    @header.setter
    def header(self, val):
        if val is None:
            self._header = self.json["Header"]

    @property
    def reads(self) -> List[Any]:
        """
        Returns read lengths
        """
        return self._reads

    @reads.setter
    def reads(self, val):
        if val is None:
            self._reads = self.json["Reads"]

    @property
    def settings(self) -> dict:
        """
        Returns analysis settings
        """
        return self._settings

    @settings.setter
    def settings(self, val):
        if val is None:
            self._settings = self.json["Settings"]

    @property
    def data(self) -> JSONType:
        """
        Returns samplesheet data
        """
        return self._data

    @data.setter
    def data(self, val):
        if val is None:
            self._data = self.json["Data"]


def flatten_record(record: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Flattens list of dicts to single dict

    Args:
        record: List of dicts

    Returns:
        a single, flattened dict
    """
    cm = ChainMap(*record)
    return dict(cm)

def parse_variant_stats_data(*filepaths: str) -> pd.DataFrame:
    """
    Parses `<SAMPLE>_CombinedVariantOutput.tsv` files, returning a `pd.DataFrame`
    object that combines all of the input together in a single dataset.

    Data frame contents currently limited to:

        - Analysis and run metadata
        - TMB (Tumour mutational burden) statistics, and;
        - MSI (Microsatellite instability) statistics

    Args:
        filepaths: filepaths as separate positional arguments

    Returns:
        a `pd.DataFrame` object combining all of the input as one dataset
    """
    dataset = []

    for f in filepaths:
        dataset.append(CombinedVariantOutput(f))

    fields = ["Analysis Details", "Sequencing Run Details", "TMB", "MSI"]
    filtered_dataset = [[record.json[field] for field in fields] for record in dataset]

    records = map(collapse_record, filtered_dataset)
    df = pd.DataFrame(records)

    numeric_cols = TMB_FIELDS + MSI_FIELDS

    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors = "coerce", downcast = "float")

    return(df)

def parse_samplesheet_data(filepath: str) -> pd.DataFrame:
    """
    Parses the TSO500 `*SampleSheet.csv` file, returning the contents
    of the *[Data]* section (i.e., the sample data) as a `pd.DataFrame` object.

    Args:
        filepath: path to samplesheet file

    Returns:
        Contents of *[Data]* section as a `pd.DataFrame` object
    """
    samplesheet = SampleSheet(filepath).data
    return pd.DataFrame(samplesheet)
