import pandas as pd
import os

def load_factors():
    path = os.path.join(os.path.dirname(__file__), 'factorsKZ.csv')
    return pd.read_csv(path)
