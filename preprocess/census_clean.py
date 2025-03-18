import pandas as pd
import numpy as np
import os

# Define file paths
input_file = r"D:\capstone project\data\censusData.csv"
output_file = r"D:\capstone project\output\yearly_censusData.csv"

# Load the census dataset
df = pd.read_csv(input_file)

# Convert REF_DATE to datetime format **before doing anything**
df["REF_DATE"] = pd.to_datetime(df["REF_DATE"], errors="coerce")

# Extract Year & Quarter separately
df["Year"] = df["REF_DATE"].dt.year
df["Quarter"] = df["REF_DATE"].dt.quarter

# Identify missing quarters for provinces (1950-Q1 to 1951-Q2)
missing_quarters = [(1950, 1), (1950, 2), (1950, 3), (1950, 4), (1951, 1), (1951, 2)]

# Get total Canada population for missing quarters
canada_population = df[(df["GEO"] == "Canada") & df["Year"].isin([1950, 1951])]

# Get provincial population percentages from 1951-Q3
province_population_1951_Q3 = df[(df["GEO"] != "Canada") & (df["Year"] == 1951) & (df["Quarter"] == 3)].copy()

# Ensure Canada population for 1951-Q3 exists
canada_1951_Q3_pop = canada_population[(canada_population["Year"] == 1951) & (canada_population["Quarter"] == 3)]["VALUE"].values
if len(canada_1951_Q3_pop) == 0:
    raise ValueError("Missing Canada population for 1951-Q3!")  # Ensure we have reference data

canada_1951_Q3_pop = canada_1951_Q3_pop[0]  # Extract actual number
province_population_1951_Q3["Share"] = province_population_1951_Q3["VALUE"] / canada_1951_Q3_pop
province_population_1951_Q3 = province_population_1951_Q3.dropna(subset=["Share"])  # Drop rows where Share is NaN

# Generate missing rows based on shares
new_rows = []
for (year, quarter) in missing_quarters:
    canada_pop_for_quarter = canada_population[(canada_population["Year"] == year) & (canada_population["Quarter"] == quarter)]["VALUE"].values
    if len(canada_pop_for_quarter) == 0:
        continue  # Skip if no Canada data available

    for _, row in province_population_1951_Q3.iterrows():
        estimated_pop = row["Share"] * canada_pop_for_quarter[0]  # Keep as float for now

        # Ensure values are properly assigned
        if pd.isna(estimated_pop) or estimated_pop == 0:
            print(f"Warning: Missing population estimate for {row['GEO']} in {year}-Q{quarter}")
            continue  # Skip problematic values

        new_rows.append({
            "REF_DATE": pd.to_datetime(f"{year}-01-01"),  # Using Yearly Data
            "GEO": row["GEO"],
            "VALUE": estimated_pop,  # Keep as float for now
            "Year": year
        })

# Convert new rows to DataFrame
new_rows_df = pd.DataFrame(new_rows)

# Append new data before sorting
df = pd.concat([df, new_rows_df], ignore_index=True)

# Aggregate data by year and region (GEO), taking the **average of all quarters**
df_yearly = df.groupby(["Year", "GEO"], as_index=False)["VALUE"].mean()

# Convert VALUE to **integer** (since population should not have decimals)
df_yearly["VALUE"] = df_yearly["VALUE"].replace(0, np.nan)  # Remove incorrect zeros
df_yearly["VALUE"] = df_yearly["VALUE"].fillna(method="bfill").fillna(method="ffill")  # Fill missing values
df_yearly["Population"] = df_yearly["VALUE"].round().astype(int)  # Convert to integer after filling
df_yearly = df_yearly.drop(columns=["VALUE"])  # Drop original column

# Rename columns
df_yearly.rename(columns={"REF_DATE": "Year"}, inplace=True)

# Map GEO to province short names
province_map = {
    "Alberta": "AB",
    "British Columbia": "BC",
    "Manitoba": "MB",
    "New Brunswick": "NB",
    "Newfoundland and Labrador": "NL",
    "Nova Scotia": "NS",
    "Ontario": "ON",
    "Prince Edward Island": "PE",
    "Quebec": "QC",
    "Saskatchewan": "SK",
    "Northwest Territories": "NT",
    "Nunavut": "NU",
    "Yukon": "YT",
    "Canada": "CA"
}
df_yearly["Province"] = df_yearly["GEO"].map(province_map)

# Ensure proper sorting by Year & Province
df_yearly = df_yearly.sort_values(by=["Year", "GEO"], ascending=[True, True])

# Remove unnecessary columns
columns_to_drop = ["DGUID", "UOM", "UOM_ID", "SCALAR_FACTOR", "SCALAR_ID", 
                   "VECTOR", "COORDINATE", "STATUS", "SYMBOL", "TERMINATED", "DECIMALS"]
df_yearly = df_yearly.drop(columns=[col for col in columns_to_drop if col in df_yearly.columns], errors="ignore")

# Save cleaned data
os.makedirs(os.path.dirname(output_file), exist_ok=True)
df_yearly.to_csv(output_file, index=False)

print(f"✅ Yearly census data saved to: {output_file}")
