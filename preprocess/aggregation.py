import os
import glob
import pandas as pd

# Directories
data_dir = r"D:\capstone project\data"
output_dir = r"D:\capstone project\output"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Pattern to match all CSV files in data_dir
file_pattern = os.path.join(data_dir, "*.csv")
file_list = glob.glob(file_pattern)

print(f"Found {len(file_list)} CSV files in {data_dir}.")

# Columns to keep
columns_to_keep = ["STATION", "NAME", "PRCP", "DATE", "SNOW", "TMIN", "TMAX"]

# List to hold cleaned data from all files
df_list = []

for file in file_list:
    try:
        # Read the CSV
        df = pd.read_csv(file)
    except Exception as e:
        print(f"Error reading {file}: {e}")
        continue
    
    # Check if both TMIN and TMAX exist in the columns; if not, skip this file
    required_cols = {"TMIN", "TMAX"}
    if not required_cols.issubset(df.columns):
        print(f"Skipping {os.path.basename(file)} because it doesn't have TMIN or TMAX columns.")
        continue
    
    # Keep only the columns of interest (that are actually present)
    keep_these = [col for col in columns_to_keep if col in df.columns]
    df = df[keep_these]
    
    # Drop rows where TMIN or TMAX is missing
    df = df.dropna(subset=["TMIN", "TMAX"])
    
    # If there's still data left after dropping, add to our list
    if not df.empty:
        df_list.append(df)

# Concatenate all cleaned DataFrames into one
if df_list:
    final_df = pd.concat(df_list, ignore_index=True)
    print(f"Combined DataFrame has {len(final_df)} rows after cleaning.")
    
    # Write the final cleaned data to a single CSV
    output_file = os.path.join(output_dir, "cleaned_data.csv")
    final_df.to_csv(output_file, index=False)
    print(f"Cleaned data saved to: {output_file}")
else:
    print("No valid data to combine after cleaning.")
