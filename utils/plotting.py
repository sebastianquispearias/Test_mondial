# utils/plotting.py
import matplotlib.pyplot as plt
import seaborn as sns

def plot_boxplot(df, x_col, y_col, hue_col=None):
    plt.figure()
    sns.boxplot(data=df, x=x_col, y=y_col, hue=hue_col)
    plt.title(f"Boxplot de {y_col} por {x_col}")
    plt.tight_layout()
    plt.show()
