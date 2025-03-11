import os
import sys
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

data_root = utils.get_data_root()
xlsx_file_path = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'C02_data_cleaned.xlsx')
df = pd.read_excel(xlsx_file_path, engine='openpyxl')

gss = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
train_idx, test_idx = next(gss.split(df, groups=df['TIF ID']))

train_data = df.iloc[train_idx]
test_data = df.iloc[test_idx]

train_file = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'C02_data_train.xlsx')
test_file = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'C02_data_test.xlsx')

train_data.to_excel(train_file, index=False)
test_data.to_excel(test_file, index=False)

print("Data splitting and saving completed.")
print(f"Training file: {train_file}")
print(f"Test file: {test_file}")
