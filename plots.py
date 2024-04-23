import seaborn as sns
import pandas as pd


# def show_

def show_scatterplot(x_values, y_values):
    data = {
        'x': x_values,
        'y': y_values
    }
    df = pd.DataFrame(data)
    sns.scatterplot(data=df, x='x', y='y')
    import matplotlib.pyplot as plt
    plt.show()
