import ee
import geopandas as gpd
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Initialize the Earth Engine API
ee.Initialize()

# Define Landsat collections and their time ranges
data_root = utils.get_data_root()
landsat_collections = {
    'LANDSAT/LT05/C02/T1_L2': (1984, 2012, 'Landsat 5'),
    'LANDSAT/LE07/C02/T1_L2': (1999, 2022, 'Landsat 7'),
    'LANDSAT/LC08/C02/T1_L2': (2013, 2021, 'Landsat 8'),
    'LANDSAT/LC09/C02/T1_L2': (2021, 2023, 'Landsat 9')
}

# Function to count images for a geometry
max_cloud_cover = 10

def count_images(collection_id, start_year, end_year, geom):
    collection = ee.ImageCollection(collection_id) \
        .filterDate(f'{start_year}-01-01', f'{end_year}-12-31') \
        .filterBounds(geom) \
        .filter(ee.Filter.lt('CLOUD_COVER', max_cloud_cover))
    return collection.size().getInfo()

# Paths for input and output
shapefile_path = data_root + 'intermediate/CPIS/SSA_CPIS.shp'  # Update with your shapefile path
pivot_id_file = os.path.join(data_root, 'intermediate/2_data_request/stratified_cp_ids.txt')  # Text file containing Pivot IDs (one per line)
log_file_path = "landsat_image_availability.log"

# Load the shapefile
center_pivots = gpd.read_file(shapefile_path)

# Load the list of Pivot IDs from the text file
with open(pivot_id_file, 'r') as f:
    pivot_ids = [line.strip() for line in f.readlines()]

# Open the log file for writing
with open(log_file_path, 'w') as log_file:
    log_file.write("Landsat Image Availability Report\n")
    log_file.write("=" * 50 + "\n")

    # Iterate over the specified Pivot IDs
    for pivot_id in pivot_ids:
        # Match the pivot ID to the corresponding geometry in the shapefile
        row = center_pivots[center_pivots['ID'] == int(pivot_id)]
        if row.empty:
            log_file.write(f"\nPivot ID: {pivot_id} - Geometry not found\n")
            print(f"Pivot ID: {pivot_id} - Geometry not found")
            continue
        
        geom = ee.Geometry.Polygon(row.iloc[0]['geometry'].__geo_interface__['coordinates'])  # Convert to EE geometry
        
        log_file.write(f"\nPivot ID: {pivot_id}\n")
        log_file.write("-" * 50 + "\n")
        print(f"Processing Pivot ID: {pivot_id}")

        # Iterate over the Landsat collections
        for collection_id, (start_year, end_year, name) in landsat_collections.items():
            try:
                count = count_images(collection_id, start_year, end_year, geom)
                log_file.write(f"  {name}: {count} images\n")
                print(f"  {name}: {count} images")
            except Exception as e:
                error_message = f"  {name}: Error ({e})"
                log_file.write(error_message + "\n")
                print(error_message)

    log_file.write("\nProcessing Complete\n")
    log_file.write("=" * 50 + "\n")

# Notify the user
print(f"\nResults written to {os.path.abspath(log_file_path)}")
