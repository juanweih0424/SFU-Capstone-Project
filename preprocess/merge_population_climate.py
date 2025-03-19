import pandas as pd
import os

# File paths
temp_file = r"D:\capstone project\output\province_temperature_stats_zscore.csv"
pop_file = r"D:\capstone project\output\yearly_censusData.csv"
output_file = r"D:\capstone project\output\merged_climate_population.csv"

# Load datasets
df_temp = pd.read_csv(temp_file)
df_pop = pd.read_csv(pop_file)

# Ensure Year column is an integer for consistency
df_temp["Year"] = df_temp["Year"].astype(int)
df_pop["Year"] = df_pop["Year"].astype(int)

# **REMOVE 2024 from both datasets**
df_temp = df_temp[df_temp["Year"] < 2024]
df_pop = df_pop[df_pop["Year"] < 2024]

# Merge datasets on "Year" and "Province"
merged_df = pd.merge(df_temp, df_pop, on=["Year", "Province"], how="inner")

# Save merged dataset
os.makedirs(os.path.dirname(output_file), exist_ok=True)
merged_df.to_csv(output_file, index=False)

print(f"✅ Merged dataset (without 2024) saved to: {output_file}")
