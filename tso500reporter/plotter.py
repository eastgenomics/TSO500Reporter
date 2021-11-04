import matplotlib.pyplot as plt
import seaborn as sns

def generate_plot(dataset, x_column, y_columns):

    fig, axes = plt.subplots(1, len(y_columns))

    for idx in range(len(y_columns)):
        sns.barplot(data=dataset, x=x_column, y=y_columns[idx], ax=axes[idx])

    for ax in fig.axes:
        plt.sca(ax)
        plt.xticks(rotation=45)
