from collections import ChainMap
import re

import pandas as pd

from .constants import TMB_FIELDS, MSI_FIELDS

class IlluminaFile(object):
    """
    Not intended to be used. Use sub-classes instead
    """
    def __init__(self, filename=None, delim=None, skip=None, tabular_sections=[], array_sections=[]):
        self.filename = filename
        self._tabular_sections = tabular_sections
        self._array_sections = array_sections
        self._delim = delim
        self._skip = skip
        self.json = None

    @property
    def json(self):
        return self.__json

    @json.setter
    def json(self, val):
        if val is None:
            self.__json = self.__read()

    def __read(self): 
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
                            rows += ["NA" for i in range(n_missing_values)]
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

    def _extract_header(self, header_string):
        return re.search('\[(.+)\]', header_string).group(1)

class CombinedVariantOutput(IlluminaFile):
    """
    docs here
    """
    def __init__(self, filename):
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
    def analysis_details(self):
        return self.__analysis_details

    @analysis_details.setter
    def analysis_details(self, val):
        if val is None:
            self.__analysis_details = self.json["Analysis Details"]

    @property
    def sequencing_run_details(self):
        return self.__sequencing_run_details

    @sequencing_run_details.setter
    def sequencing_run_details(self, val):
        if val is None:
            self.__sequencing_run_details = self.json["Sequencing Run Details"]

    @property
    def tmb(self):
        return self.__tmb

    @tmb.setter
    def tmb(self, val):
        if val is None:
            self.__tmb = self.json["TMB"]

    @property
    def msi(self):
        return self.__msi

    @msi.setter
    def msi(self, val):
        if val is None:
            self.__msi = self.json["MSI"]

    @property
    def gene_amplifications(self):
        return self.__gene_amplifications

    @gene_amplifications.setter
    def gene_amplifications(self, val):
        if val is None:
            self.__gene_amplifications = self.json["Gene Amplifications"]

    @property
    def splice_variants(self):
        return self.__splice_variants

    @splice_variants.setter
    def splice_variants(self, val):
        if val is None:
            self.__splice_variants = self.json["Splice Variants"]

    @property
    def fusions(self):
        return self.__fusions

    @fusions.setter
    def fusions(self, val):
        if val is None:
            self.__fusions = self.json["Fusions"]

    @property
    def small_variants(self):
        return self.__small_variants

    @small_variants.setter
    def small_variants(self, val):
        if val is None:
            self.__small_variants = self.json["Small Variants"]


class SampleSheet(IlluminaFile):
    """
    docs here
    """
    def __init__(self, filename):
        super().__init__(filename, delim=",", tabular_sections=["Data"], array_sections=["Reads"], skip=0)
        self.header = None
        self.reads = None
        self.settings = None
        self.data = None

    @property
    def header(self):
        return self.__header

    @header.setter
    def header(self, val):
        if val is None:
            self.__header = self.json["Header"]

    @property
    def reads(self):
        return self.__reads

    @reads.setter
    def reads(self, val):
        if val is None:
            self.__reads = self.json["Reads"]

    @property
    def settings(self):
        return self.__settings

    @settings.setter
    def settings(self, val):
        if val is None:
            self.__settings = self.json["Settings"]

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, val):
        if val is None:
            self.__data = self.json["Data"]

def collapse_record(record):
    """
    docs here
    """
    cm = ChainMap(*record)
    return dict(cm)

def parse_variant_stats_data(*files):
    """
    docs here
    """
    dataset = []

    for f in files:
        dataset.append(CombinedVariantOutput(f))

    fields = ["Analysis Details", "Sequencing Run Details", "TMB", "MSI"]
    filtered_dataset = [[record.json[field] for field in fields] for record in dataset]

    records = map(collapse_record, filtered_dataset)
    df = pd.DataFrame(records)

    numeric_cols = TMB_FIELDS + MSI_FIELDS

    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors = "coerce", downcast = "float")

    return(df)
