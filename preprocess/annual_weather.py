import pandas as pd
import numpy as np
from tqdm import tqdm
import os

# Initialize tqdm for pandas
tqdm.pandas()

# Define paths
input_path = r"D:\capstone project\output\aggregateData_clean.csv"
output_dir = r"D:\capstone project\output"
output_flags_path = os.path.join(output_dir, "data_with_zscore_flags.csv")
output_stats_path = os.path.join(output_dir, "province_temperature_stats_zscore.csv")

# Create output directory if needed
os.makedirs(output_dir, exist_ok=True)

# Load data with optimized dtypes
df = pd.read_csv(input_path, dtype={
    'STATION': 'category',
    'PRCP': 'float32',
    'SNOW': 'float32',
    'TWIN': 'float32',
    'TMAX': 'float32',
    'TAVG': 'float32'
})

# 1. Extract province from NAME column
def extract_province(name):
    parts = str(name).split(', ')[-1].split()
    return parts[0] if len(parts) >= 2 else None

df['Province'] = df['NAME'].apply(extract_province)

# 2. Extract year from DATE column
df['DATE'] = pd.to_datetime(df['DATE'])
df['Year'] = df['DATE'].dt.year

# 3. Clean data - remove rows with missing temperature values
temp_cols = ['TAVG', 'TMAX', 'TMIN']
df_clean = df.dropna(subset=temp_cols)

# 4. Z-score outlier detection (per province and year)
Z_SCORE_THRESHOLD = 3

def calculate_zscore(df_group):
    for col in temp_cols:
        mean = df_group[col].mean()
        std = df_group[col].std()
        df_group[f'{col}_zscore'] = np.where(
            std != 0,
            (df_group[col] - mean) / std,
            0
        )
    return df_group

# Calculate z-scores with progress tracking
df_clean = df_clean.groupby(['Province', 'Year'], group_keys=False).progress_apply(calculate_zscore)

# Flag outliers in any temperature column
outlier_flags = [
    (df_clean[f'{col}_zscore'].abs() > Z_SCORE_THRESHOLD)
    for col in temp_cols
]
df_clean['is_outlier'] = np.any(outlier_flags, axis=0)

# 5. Save flagged data for inspection
df_clean.to_csv(output_flags_path, index=False)
print(f"Z-score flagged data saved to: {output_flags_path}")

# 6. Filter out outliers and reset index
df_filtered = df_clean[~df_clean['is_outlier']].reset_index(drop=True)

# 7. Calculate annual statistics (with index ambiguity fix)
result = df_filtered.groupby(['Province', 'Year'], as_index=False).agg({
    'TAVG': 'mean',
    'TMAX': 'max',
    'TMIN': 'min',
    'STATION': pd.Series.nunique
}).rename(columns={
    'TAVG': 'Annual_Mean_Temp',
    'TMAX': 'Annual_Max_Temp',
    'TMIN': 'Annual_Min_Temp',
    'STATION': 'Station_Count'
})

# Formatting
result = result.round({
    'Annual_Mean_Temp': 2,
    'Annual_Max_Temp': 1,
    'Annual_Min_Temp': 1
})

# 8. Save final statistics
result.to_csv(output_stats_path, index=False)
print(f"Temperature statistics saved to: {output_stats_path}")

print("\nProcess Summary:")
print(f"Total records processed: {len(df)}")
print(f"Outliers removed: {df_clean['is_outlier'].sum()}")
print(f"Valid records remaining: {len(df_filtered)}")