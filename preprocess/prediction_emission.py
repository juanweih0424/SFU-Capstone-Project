import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# File paths
climate_path = r"D:\capstone project\output\merged_climate_population.csv"
emissions_path = r"D:\capstone project\output\aggregated_emissions_by_province_year.csv"
output_path = r"D:\capstone project\output\ghgrp_emissions_1950_2023_predicted.csv"

# Load datasets
climate_pop_df = pd.read_csv(climate_path)
emissions_df = pd.read_csv(emissions_path)

# Province code to full name mapping
province_code_map = {
    'AB': 'Alberta', 'BC': 'British Columbia', 'MB': 'Manitoba',
    'NB': 'New Brunswick', 'NL': 'Newfoundland and Labrador', 'NS': 'Nova Scotia',
    'NT': 'Northwest Territories', 'NU': 'Nunavut', 'ON': 'Ontario',
    'PE': 'Prince Edward Island', 'QC': 'Quebec', 'SK': 'Saskatchewan',
    'YT': 'Yukon'
}

# Ensure matching province names
climate_pop_df['Province'] = climate_pop_df['Province'].replace(province_code_map)

# Merge emissions with climate+population data on Province and Year
merged_df = pd.merge(emissions_df, climate_pop_df, on=['Province', 'Year'])

# Encode province names for the model
le = LabelEncoder()
merged_df['Province_Code'] = le.fit_transform(merged_df['Province'])

# Features for model training
features = ['Province_Code', 'Year', 'Annual_Mean_Temp', 'Annual_Max_Temp',
            'Annual_Min_Temp', 'Station_Count', 'Population']
X = merged_df[features]
y = merged_df['Emissions']

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Predict emissions for 1950–2003
prediction_df = climate_pop_df[climate_pop_df['Year'] < 2004].copy()
prediction_df['Province_Code'] = le.transform(prediction_df['Province'])

X_pred = prediction_df[features]
prediction_df['Emissions'] = model.predict(X_pred)

# Keep only necessary columns
predicted_emissions_df = prediction_df[['Province', 'Year', 'Emissions']]

# Combine predicted and actual emissions
actual_emissions_df = merged_df[['Province', 'Year', 'Emissions']]
full_emissions_df = pd.concat([predicted_emissions_df, actual_emissions_df], axis=0)

# Merge with original climate_pop_df
final_output_df = pd.merge(climate_pop_df, full_emissions_df, on=['Province', 'Year'], how='left')

# Save the final dataset
final_output_df.to_csv(output_path, index=False)
print(f"Saved merged dataset with emissions to: {output_path}")
