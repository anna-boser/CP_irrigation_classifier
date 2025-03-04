import json
import rasterio
import pandas as pd
import os
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Directory containing the TIF files
data_root = utils.get_data_root()
# Step 1: Read JSON File
json_file_path = os.path.join(data_root, 'intermediate/4_data_pipeline/training_C02_label_data.json')
with open(json_file_path, 'r') as json_file:
    annotations_data = json.load(json_file)

# Step 2: Create a mapping of image filenames to annotation data
image_to_annotation = {}
tif_name_to_id = {}
current_tif_id = 1

for annotation in annotations_data:
    # Example: annotation['data']['filename'] -> "CP_10168_Landsat7_2001-02-17_RGB.jpg"
    if 'data' not in annotation or 'filename' not in annotation['data']:
        print("Skipping annotation without 'data.filename' field.")
        continue

    filename = annotation['data']['filename']
    base = filename.replace("_RGB.jpg", "")  # -> "CP_10168_Landsat7_2001-02-17"

    parts = base.split("_")  # Expect ["CP", "10168", "Landsat7", "2001-02-17"]
    if len(parts) < 4:
        print(f"Skipping annotation with unexpected filename format: {filename}")
        continue

    pivot_id = parts[1]          # "10168"
    landsat_version = parts[2]   # "Landsat7"
    ymd = parts[3].split("-")    # ["2001", "02", "17"]
    if len(ymd) < 3:
        print(f"Skipping annotation with unexpected date format: {filename}")
        continue

    year, month, day = ymd

    # Create a unique key
    key = (pivot_id, landsat_version, year, month, day)

    if key not in tif_name_to_id:
        tif_name_to_id[key] = current_tif_id
        current_tif_id += 1

    image_to_annotation[key] = annotation


# Step 3: Read the band names from the text file
band_names = {}
with open(os.path.join(data_root, 'intermediate/4_data_pipeline/band_names_training.txt'), 'r') as band_names_file:
    current_tif_name = None
    for line in band_names_file:
        if line.startswith('Band names for '):
            current_tif_name = line.split('Band names for ')[1].strip().split('.')[0]
            band_names[current_tif_name] = []
        elif line.startswith('Band '):
            band_names[current_tif_name].append(line.split(': ')[1].strip())

# Step 4: Prepare DataFrame
data = []
columns = ['TIF ID', 'TIF Name', 'Landsat', 'Year', 'Month', 'Day', 'X Value', 'Y Value', 'Label', 'X-Coord', 'Y-Coord',
           'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15', 'B16', 'B17', 'B18', 'B19']

tif_folder = os.path.join(data_root, 'intermediate/training_data_C02')
geojson_folder = os.path.join(data_root, 'intermediate/4_data_pipeline/collection_2_geojson') 
for tif_filename in os.listdir(tif_folder):
    if not tif_filename.endswith('.tif'):
        continue

    # Extract pivot_id, landsat_name, year, month, and day from the new filename format
    parts = tif_filename.split('_')
    pivot_id = parts[1]
    landsat_name = parts[2]
    year, month, day = parts[3].split('-')
    day = day.split('.')[0]
    key = (pivot_id, landsat_version, year, month, day)

    if key not in image_to_annotation:
        continue

    annotation = image_to_annotation[key]
    tif_file_path = f'{tif_folder}/{tif_filename}'
    with rasterio.open(tif_file_path) as src:
        band_data = ['N/A'] * 19  # Ensure you have 19 bands to read

        # Get the GeoJSON filename
        geojson_filename = f'{tif_filename.split(".tif")[0]}.geojson'
        geojson_file_path = os.path.join(geojson_folder, geojson_filename)

        # Open the GeoJSON file
        with open(geojson_file_path, 'r') as geojson_file:
            geojson_data = json.load(geojson_file)

        bottom_left = geojson_data['features'][0]['geometry']['coordinates'][0][0]
        top_right = geojson_data['features'][0]['geometry']['coordinates'][0][2]

        # Extract annotation data 
        annotation_list = annotation.get('annotations', [])
        if annotation_list:
            for result in annotation_list[0]['result']:
                if result['type'] == 'keypointlabels':
                    x_percent = result['value']['x']
                    y_percent = result['value']['y']
                    label = result['value']['keypointlabels'][0]

                    # Convert percentage to pixel coordinates
                    x_pixel = int(x_percent * src.width / 100)
                    y_pixel = int(y_percent * src.height / 100)
                    x = bottom_left[0] + (top_right[0] - bottom_left[0]) * (x_percent / 100)
                    y = bottom_left[1] + (top_right[1] - bottom_left[1]) * (y_percent / 100)

                    # Extract the first 19 bands from the TIFF image
                    for i in range(19):  # Assuming you want the first 19 bands
                        band_index = i + 1  # Band indices in rasterio are 1-based
                        band = src.read(band_index, window=((y_pixel, y_pixel+1), (x_pixel, x_pixel+1)))
                        if band.size > 0:
                            band_data[i] = band[0, 0]

                    # Append data to list
                    tif_id = tif_name_to_id[key]  
                    row = [tif_id, tif_filename, landsat_name, year, month, day, x_percent, y_percent, label, x, y] + band_data  
                    data.append(row)
# Step 5: Write data to Excel file
df = pd.DataFrame(data, columns=columns)
excel_file_path = os.path.join(data_root, 'intermediate/4_data_pipeline/C02_data_unsplit.xlsx') 
df.to_excel(excel_file_path, index=False)