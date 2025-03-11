import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# 1) Get data root and define the Excel file path
data_root = utils.get_data_root()
excel_file_path = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'C02_data_unsplit.xlsx')

# 2) Load the Excel file
df = pd.read_excel(excel_file_path)

# 3) Dictionary of band MEANINGS for Landsat 5, 7, and 8
band_meanings = {
    "Landsat5": {
        "B1": "Blue",
        "B2": "Green",
        "B3": "Red",
        "B4": "NIR",
        "B5": "SWIR1",
        "B6": "SWIR2",
        "B7": "Atmos_Opacity",
        "B8": "Cloud_QA",
        "B9": "Thermal",
        "B10": "ST_ATRAN",
        "B11": "ST_CDIST",
        "B12": "ST_DRAD",
        "B13": "ST_EMIS",
        "B14": "ST_EMSD",
        "B15": "ST_QA",
        "B16": "ST_TRAD",
        "B17": "ST_URAD",
        "B18": "QA_PIXEL",
        "B19": "QA_RADSAT"
    },
    "Landsat7": {
        "B1": "Blue",
        "B2": "Green",
        "B3": "Red",
        "B4": "NIR",
        "B5": "SWIR1",
        "B6": "SWIR2",
        "B7": "Atmos_Opacity",
        "B8": "Cloud_QA",
        "B9": "Thermal",
        "B10": "ST_ATRAN",
        "B11": "ST_CDIST",
        "B12": "ST_DRAD",
        "B13": "ST_EMIS",
        "B14": "ST_EMSD",
        "B15": "ST_QA",
        "B16": "ST_TRAD",
        "B17": "ST_URAD",
        "B18": "QA_PIXEL",
        "B19": "QA_RADSAT"
    },
    "Landsat8": {
        "B1": "CoastalAerosol",
        "B2": "Blue",
        "B3": "Green",
        "B4": "Red",
        "B5": "NIR",
        "B6": "SWIR1",
        "B7": "SWIR2",
        "B8": "QA_Aerosol",
        "B9": "Thermal",
        "B10": "ST_ATRAN",
        "B11": "ST_CDIST",
        "B12": "ST_DRAD",
        "B13": "ST_EMIS",
        "B14": "ST_EMSD",
        "B15": "ST_QA",
        "B16": "ST_TRAD",
        "B17": "ST_URAD",
        "B18": "QA_PIXEL",
        "B19": "QA_RADSAT"
    }
}

# 4) Create new columns for all possible band meanings
all_new_cols = set()
for rename_map in band_meanings.values():
    all_new_cols.update(rename_map.values())

# If a column doesn't exist yet, create it (filled with NaN)
for col in all_new_cols:
    if col not in df.columns:
        df[col] = pd.NA

# 5) Copy data from B# columns into the new meaning columns
for version, rename_map in band_meanings.items():
    mask = df["Landsat"] == version
    for old_col, new_col in rename_map.items():
        if old_col in df.columns:
            # Only copy for the rows matching this version
            df.loc[mask, new_col] = df.loc[mask, old_col]


all_old_cols = set()
for vmap in band_meanings.values():
    all_old_cols.update(vmap.keys())

df.drop(columns=list(all_old_cols & set(df.columns)), inplace=True, errors='ignore')

# 6) Save the updated DataFrame back to Excel
df.to_excel(excel_file_path, index=False)

print("Excel file has been updated with new columns for each band meaning (including CoastalAerosol).")
