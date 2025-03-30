import pandas as pd

# Load the GHGRP dataset
ghgrp_path = r"D:\capstone project\data\emission.csv"
ghgrp_df = pd.read_csv(ghgrp_path)

# Aggregate emissions by Province and Year
emissions_by_province_year = (
    ghgrp_df.groupby(['Province / territory', 'Year'])['Total']
    .sum()
    .reset_index()
)

# Rename columns for clarity
emissions_by_province_year.rename(
    columns={'Province / territory': 'Province', 'Total': 'Emissions'},
    inplace=True
)

# Save to CSV
output_path = r"D:\capstone project\output\aggregated_emissions_by_province_year.csv"
emissions_by_province_year.to_csv(output_path, index=False)

print(f"Aggregated emissions saved to: {output_path}")
