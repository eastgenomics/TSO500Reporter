from collections import ChainMap
import re

import pandas as pd

from .constants import TMB_FIELDS, MSI_FIELDS

def extract_header(header_string):
    return re.search('\[(.+)\]', header_string).group(1)

def read_combined_variant_output_file(filename):
    """
    docs here
    """

    with open(filename, "r") as f:

        data = {}

        # SKIP LOGGING LINES
        next(f)
        next(f)

        for line in f:

            line = line.rstrip("\n")

            # if line is made of two tabs, the section is over
            # and the next line is a section header
            if line == "\t\t":
                header_line = True
                continue

            # PARSE HEADER DATA
            ## Extract the header name and make it a dictionary key
            if header_line:

                header = extract_header(line)
                header_line = False

                ## The named sections are TSV formatted.
                ## This means the line after the section header is the
                ## header of the TSV data.
                ## The extra f.readline() bit handles this so the next line
                ## can be handled like normal data.
                if header in ["Gene Amplifications", "Splice Variants", "Fusions", "Small Variants"]:
                    column_names = f.readline().rstrip().split("\t")
                    data[header] = [] # list of dicts for TSV formatted sections
                else:
                    data[header] = {} # regular old dict for key-value sections
                continue

            # PARSE SECTION DATA
            ## Again, these four sections are TSV formatted. We extract
            ## and put into list of dicts, with the section data header as keys
            if header in ["Gene Amplifications", "Splice Variants", "Fusions", "Small Variants"]:
                column_values = line.split("\t")

                ## For empty lines, TSO500 returns just a single "NA" instead of
                ## multiple NAs. We'll lose header information if they aren't
                ## converted from implicit missing data to explicit missing data
                if column_values[0] == "NA":
                    column_values = ["" for i in range(len(column_names))]

                ## fill list of dicts
                data[header].append(dict(zip(column_names, column_values)))

            ## Non-TSV formatted KV pairs can be dict'd normally
            else:
                section_data = line.split("\t")
                key = section_data[0]
                value = section_data[1]
                data[header][key] = value

        return(data)

def collapse_record(record):
    """
    docs here
    """
    cm = ChainMap(*record)
    return dict(cm)

def parse_data(*files):
    """
    docs here
    """
    dataset = []

    for f in files:
        dataset.append(read_combined_variant_output_file(f))

    fields = ["Analysis Details", "Sequencing Run Details", "TMB", "MSI"]
    filtered_dataset = [[record[field] for field in fields] for record in dataset]

    records = map(collapse_record, filtered_dataset)
    df = pd.DataFrame(records)

    numeric_cols = TMB_FIELDS + MSI_FIELDS

    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors = "coerce", downcast = "float")

    return(df)
