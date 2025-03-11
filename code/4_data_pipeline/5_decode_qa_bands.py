import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

data_root = utils.get_data_root()
xlsx_file_path = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'C02_data_unsplit.xlsx')
df = pd.read_excel(xlsx_file_path, engine='openpyxl')

qa_columns = ['SR_CLOUD_QA', 'QA_PIXEL', 'QA_RADSAT', 'SR_QA_AEROSOL']
for col in qa_columns:
    if col in df.columns:
        df[col] = df[col].fillna(0).astype(int, errors='ignore')

existing_cols = list(df.columns)

def decode_sr_cloud_qa_l57(value):
    return {
        'DDV':               bool(value & (1 << 0)),
        'Cloud':             bool(value & (1 << 1)),
        'Cloud_Shadow':      bool(value & (1 << 2)),
        'Adjacent_to_Cloud': bool(value & (1 << 3)),
        'Snow':              bool(value & (1 << 4)),
        'Water':             bool(value & (1 << 5))
    }

def decode_qa_pixel_l57(value):
    decoded = {}
    decoded['Fill']          = bool(value & (1 << 0))
    decoded['Dilated_Cloud'] = bool(value & (1 << 1))
    decoded['Cloud']         = bool(value & (1 << 3))
    decoded['Cloud_Shadow']  = bool(value & (1 << 4))
    decoded['Snow']          = bool(value & (1 << 5))
    decoded['Clear']         = bool(value & (1 << 6))
    decoded['Water']         = bool(value & (1 << 7))
    cc = (value >> 8) & 0b11
    decoded['Cloud_Confidence'] = {0: 'None', 1: 'Low', 2: 'Medium', 3: 'High'}.get(cc, 'Unknown')
    csc = (value >> 10) & 0b11
    decoded['Cloud_Shadow_Confidence'] = {0: 'None', 1: 'Low', 2: 'Medium', 3: 'High'}.get(csc, 'Unknown')
    sc = (value >> 12) & 0b11
    decoded['Snow_Confidence'] = {0: 'None', 1: 'Low', 2: 'Medium', 3: 'High'}.get(sc, 'Unknown')
    cir = (value >> 14) & 0b11
    decoded['Cirrus_Confidence'] = {0: 'None', 1: 'Low', 2: 'Medium', 3: 'High'}.get(cir, 'Unknown')
    return decoded

def decode_qa_radsat_l57(value):
    return {
        'Band1_Sat': bool(value & (1 << 0)),
        'Band2_Sat': bool(value & (1 << 1)),
        'Band3_Sat': bool(value & (1 << 2)),
        'Band4_Sat': bool(value & (1 << 3)),
        'Band5_Sat': bool(value & (1 << 4)),
        'Band6L_Sat': bool(value & (1 << 5)),
        'Band7_Sat': bool(value & (1 << 6)),
        'Band6H_Sat': bool(value & (1 << 8)),
        'Dropped_Pixel': bool(value & (1 << 9))
    }

def decode_qa_pixel_l8(value):
    decoded = {}
    decoded['Fill']          = bool(value & (1 << 0))
    decoded['Dilated_Cloud'] = bool(value & (1 << 1))
    decoded['Cirrus']        = bool(value & (1 << 2))
    decoded['Cloud']         = bool(value & (1 << 3))
    decoded['Cloud_Shadow']  = bool(value & (1 << 4))
    decoded['Snow']          = bool(value & (1 << 5))
    decoded['Clear']         = bool(value & (1 << 6))
    decoded['Water']         = bool(value & (1 << 7))
    cc = (value >> 8) & 0b11
    decoded['Cloud_Confidence'] = {0: 'None', 1: 'Low', 2: 'Medium', 3: 'High'}.get(cc, 'Unknown')
    csc = (value >> 10) & 0b11
    decoded['Cloud_Shadow_Confidence'] = {0: 'None', 1: 'Low', 2: 'Medium', 3: 'High'}.get(csc, 'Unknown')
    sc = (value >> 12) & 0b11
    decoded['Snow_Confidence'] = {0: 'None', 1: 'Low', 2: 'Medium', 3: 'High'}.get(sc, 'Unknown')
    cir = (value >> 14) & 0b11
    decoded['Cirrus_Confidence'] = {0: 'None', 1: 'Low', 2: 'Medium', 3: 'High'}.get(cir, 'Unknown')
    return decoded

def decode_qa_radsat_l8(value):
    return {
        'Band1_Sat': bool(value & (1 << 0)),
        'Band2_Sat': bool(value & (1 << 1)),
        'Band3_Sat': bool(value & (1 << 2)),
        'Band4_Sat': bool(value & (1 << 3)),
        'Band5_Sat': bool(value & (1 << 4)),
        'Band6_Sat': bool(value & (1 << 5)),
        'Band7_Sat': bool(value & (1 << 6)),
        'Band9_Sat': bool(value & (1 << 8)),
        'Terrain_Occlusion': bool(value & (1 << 11))
    }

def decode_sr_qa_aerosol_l8(value):
    decoded = {}
    decoded['Fill']          = bool(value & (1 << 0))
    decoded['Aerosol_Valid'] = bool(value & (1 << 1))
    decoded['Water']         = bool(value & (1 << 2))
    decoded['Interpolated']  = bool(value & (1 << 5))
    aer = (value >> 6) & 0b11
    decoded['Aerosol_Level'] = {0: 'Climatology', 1: 'Low', 2: 'Medium', 3: 'High'}.get(aer, 'Unknown')
    return decoded

def decode_qa_bands(row):
    version = row.get('Landsat', None)
    if version in ['Landsat5', 'Landsat7']:
        if 'SR_CLOUD_QA' in row:
            decoded = decode_sr_cloud_qa_l57(row['SR_CLOUD_QA'])
            for k, v in decoded.items():
                row[f'SR_CLOUD_QA_{k}'] = v
        if 'QA_PIXEL' in row:
            decoded = decode_qa_pixel_l57(row['QA_PIXEL'])
            for k, v in decoded.items():
                row[f'QA_PIXEL_{k}'] = v
        if 'QA_RADSAT' in row:
            decoded = decode_qa_radsat_l57(row['QA_RADSAT'])
            for k, v in decoded.items():
                row[f'QA_RADSAT_{k}'] = v
    elif version == 'Landsat8':
        if 'QA_PIXEL' in row:
            decoded = decode_qa_pixel_l8(row['QA_PIXEL'])
            for k, v in decoded.items():
                row[f'QA_PIXEL_{k}'] = v
        if 'QA_RADSAT' in row:
            decoded = decode_qa_radsat_l8(row['QA_RADSAT'])
            for k, v in decoded.items():
                row[f'QA_RADSAT_{k}'] = v
        if 'SR_QA_AEROSOL' in row:
            decoded = decode_sr_qa_aerosol_l8(row['SR_QA_AEROSOL'])
            for k, v in decoded.items():
                row[f'SR_QA_AEROSOL_{k}'] = v
    return row

df = df.apply(decode_qa_bands, axis=1)

all_cols = list(df.columns)
new_cols = [c for c in all_cols if c not in existing_cols]
df = df[existing_cols + new_cols]

output_xlsx = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'C02_data_qa_decoded.xlsx')
df.to_excel(output_xlsx, index=False)
print(f"Decoded QA bands saved to: {output_xlsx}")
