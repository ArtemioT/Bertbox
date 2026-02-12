import pandas as pd
import os

#put the file you want to convert into data folder and specify your path in file
file = "data/real.xls"

df = pd.read_excel(file, engine="xlrd")

df.to_csv("data/converted.csv") #put the name of the .csv into this string