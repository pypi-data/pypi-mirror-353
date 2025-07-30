import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def load_and_plot_housing_data():
    from sklearn.datasets import fetch_california_housing
    data = fetch_california_housing(as_frame=True)
    df = data.frame
    sns.pairplot(df.head(100))
    plt.show()
