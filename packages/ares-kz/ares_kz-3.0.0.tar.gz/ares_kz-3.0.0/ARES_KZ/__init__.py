import os
import pandas as pd

def load_kz_data():
    path = os.path.join(os.path.dirname(__file__), "factorsKZ.csv")
    return pd.read_csv(path)