import matplotlib.pyplot as plt
import seaborn as sns

def generate_plot(dataset, x_column, y_columns, fwidth=25, fheight=10):

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
