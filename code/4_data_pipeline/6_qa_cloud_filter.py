import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

data_root = utils.get_data_root()
decoded_xlsx = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'C02_data_qa_decoded.xlsx')
df = pd.read_excel(decoded_xlsx, engine='openpyxl')

def is_good_data(row):
    v = row.get('Landsat', None)

    if v in ['Landsat5', 'Landsat7']:
        # Filter out rows if key flags indicate definite cloud/invalid data
        if any([
            row.get('SR_CLOUD_QA_Cloud') is True,
            row.get('SR_CLOUD_QA_Cloud_Shadow') is True,
            row.get('QA_PIXEL_Fill') is True,
            row.get('QA_PIXEL_Cloud') is True,
            row.get('QA_PIXEL_Cloud_Shadow') is True,
            row.get('QA_PIXEL_Water') is True, 
            row.get('QA_PIXEL_Clear') is False,
            row.get('QA_PIXEL_Cloud_Confidence') == 'High'
        ]):
            return False

    elif v == 'Landsat8':
        if any([
            row.get('QA_PIXEL_Fill') is True,
            row.get('QA_PIXEL_Cirrus') is True,
            row.get('QA_PIXEL_Cloud') is True,
            row.get('QA_PIXEL_Cloud_Shadow') is True,
            row.get('QA_PIXEL_Water') is True, 
            row.get('QA_PIXEL_Clear') is False,
            row.get('QA_PIXEL_Cloud_Confidence') == 'High'
        ]):
            return False

    return True

df_filtered = df[df.apply(is_good_data, axis=1)]

output_xlsx = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'C02_data_no_clouds.xlsx')
df_filtered.to_excel(output_xlsx, index=False)
print(f"Filtered dataset saved to: {output_xlsx}")
