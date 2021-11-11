"""
Generates barplots of submitted data
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List

def generate_plot(dataset: pd.DataFrame, x_column: str, y_columns: List[str], fwidth:int=25, fheight:int=10) -> plt.figure:
    """
    Generates barplots given a dataframe. If multiple y-axis columns are specified,
    multiple subplots will be generated and returned as part of the overall figure. 
    Returns the figure as an object.

    Args:
        dataset: a `pd.DataFrame` object
        x_column: x axis variable
        y_columns: y axis variables. If multiple y columns are specified, each will
            be plotted within its own subplot.
        fwidth: figure width in inches
        fheight: figure height in inches

    Returns:
        The plot as a `plt.figure` object
    """
    fig, axes = plt.subplots(1, len(y_columns), figsize=(fwidth, fheight))

    for idx in range(len(y_columns)):
        sns.barplot(data=dataset, x=x_column, y=y_columns[idx], ax=axes[idx])

    for ax in fig.axes:
        xlabels = ax.get_xticklabels()
        ax.set_xticklabels(xlabels, rotation=40, ha="right")
        y_axis_title = ax.get_ylabel()
        ax.yaxis.label.set_visible(False)
        ax.set_title(y_axis_title)


    return fig
