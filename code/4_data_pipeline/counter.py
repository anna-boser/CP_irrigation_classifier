import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

data_root = utils.get_data_root()
xlsx_file_path = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'C02_data_cleaned.xlsx')

df = pd.read_excel(xlsx_file_path, engine='openpyxl')

print("Rows per Landsat version:")
print(df['Landsat'].value_counts())

print("\nRows per Label ID:")
print(df['Label ID'].value_counts())
