import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

data_root = utils.get_data_root()
filtered_xlsx = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'C02_data_no_clouds.xlsx')
df = pd.read_excel(filtered_xlsx, engine='openpyxl')

# Columns you definitely want to keep
columns_to_keep = [
    "TIF ID", "TIF Name", "Landsat", "Year", "Month", "Day", "X Value", "Y Value",
    "Label", "X-Coord", "Y-Coord", "Red", "Blue", "SWIR1", "Thermal", "NIR",
    "Green", "SWIR2"
]

# Optional columns (ST_* bands) that you might include for training
optional_st_columns = [
    "ST_TRAD", "ST_ATRAN", "ST_URAD", "ST_CDIST",
    "ST_EMIS", "ST_DRAD", "ST_EMSD", "ST_QA"
]

# Decide whether to keep these ST_* columns
include_st_bands = True

if include_st_bands:
    columns_to_keep += optional_st_columns

# Filter down to just those columns if they exist
final_cols = [col for col in columns_to_keep if col in df.columns]
df_cleaned = df[final_cols]

cleaned_xlsx = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'C02_data_cleaned.xlsx')
df_cleaned.to_excel(cleaned_xlsx, index=False)
print(f"Cleaned dataset saved to: {cleaned_xlsx}")
