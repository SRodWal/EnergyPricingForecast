#Import general modules
import pandas as pd
import os
import numpy as np

#Import dedicated modules
from fourier.quick_fourier import decompose_hourly_by_year


#Inital Parameters (Years)
year_list = [2022,2023,2024,2025]
year = 2025

#Read_Raw File
df_dir = r'C:\Users\serw1\OneDrive - RodWal\Professional_WorkTools\Github\EnergyPricingForecast\data\raw\hourly_prices.xlsx'
df = pd.read_excel(df_dir, sheet_name = 'cleaned', engine = 'openpyxl') #Hours named DateTime, prices named DailyAvg_Median
print("File Columns: ",df.columns)

for year in year_list:
    mini_df = df.loc[df['DateTime - Year'] == year]
    mini_df["DateTime"] = pd.to_datetime(mini_df["DateTime"])
    mini_df = mini_df.sort_values("DateTime").set_index("DateTime")
    mini_df = mini_df.rename(columns = {'DailyAvg_Median':'price'})
    mini_df = mini_df[['price']]

    #Coefficient Decomposition
    res = decompose_hourly_by_year(mini_df, price_col="price", enforce_hourly=False)
    a = res[year]["a"]
    b = res[year]["b"]
    N = res[year]["N"]
    index = res[year]["index"]
    raw = res[year]["raw"]

    coef_df = pd.DataFrame({
        "year": year,
        "n": np.arange(len(a)),
        "a_n": a,
        "b_n": b,
        "amplitude": np.sqrt(a**2 + b**2),
        "period_hours": [np.inf if n == 0 else N / n for n in range(len(a))]
    })

    print("Export Coefficients for Sim - ,",year)
    coef_df.to_csv(
        rf"data\results\coef_simulation_{year}.csv",
        index_label="DateTime")