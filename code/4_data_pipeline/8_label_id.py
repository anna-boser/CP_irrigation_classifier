import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

data_root = utils.get_data_root()
xlsx_file_path = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'C02_data_cleaned.xlsx')
df = pd.read_excel(xlsx_file_path, engine='openpyxl')

def label_to_id(label):
    if "Unirr" in str(label):
        return 0
    elif "Irr" in str(label):
        return 1
    return None

df['Label ID'] = df['Label'].apply(label_to_id)

col_list = df.columns.tolist()
if 'Label ID' in col_list:
    label_id_index = col_list.index('Label ID')
    col_list.insert(7, col_list.pop(label_id_index))
    df = df[col_list]

output_path = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'C02_data_cleaned.xlsx')
df.to_excel(output_path, index=False)
print(f"Saved dataset with 'Label ID' column to: {output_path}")
