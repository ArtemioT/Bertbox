import pandas as pd
import os

file = "data/real.xls"

df = pd.read_excel(file, engine="xlrd")
df.to_csv("data/converted.csv")