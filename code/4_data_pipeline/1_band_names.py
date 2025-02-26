import os
import rasterio
import sys 
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
import utils

# Directory containing the TIF files
data_root = utils.get_data_root()
tif_directory = os.path.join(data_root, 'intermediate/2_data_request/training_data_C02')

# Output file path
output_file_path = os.path.join(data_root, 'intermediate/4_data_pipeline/band_names_training.txt')

# Open the output file in write mode
with open(output_file_path, 'w') as output_file:
    # Iterate over the TIF files
    for tif_name in os.listdir(tif_directory):
        if tif_name.endswith('.tif'):
            tif_path = os.path.join(tif_directory, tif_name)
            output_file.write(f"Band names for {tif_name}:\n")
            with rasterio.open(tif_path) as src:
                for i, name in zip(src.indexes, src.descriptions):
                    output_file.write(f"Band {i}: {name}\n")