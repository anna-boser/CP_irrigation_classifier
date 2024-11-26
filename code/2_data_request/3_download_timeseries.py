import logging
from exporter_class import LandsatDataExporter
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

'''Modified script to begin with pivot IDs from a provided text file and continue with the rest.'''

# Initialize parameters
data_root = utils.get_data_root()
shapefile_path = data_root + 'intermediate/CPIS/SSA_CPIS.shp'
drive_folder = 'landsat_timeseries_request'
log_name = 'landsat_full_request.log'
completed_pivot_file = 'completed_pivots.txt'
input_pivot_file = data_root + '2_data_request/stratified_cp_ids.txt'
max_cloud_cover = 100  # Set to 100 to ensure no images are missed

# Setup logging
logging.basicConfig(filename=log_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the exporter
exporter = LandsatDataExporter(shapefile_path, drive_folder)
logging.info('Initialized LandsatDataExporter')

# Generate a list of pivot IDs
all_pivot_ids = exporter.center_pivot_gdf['ID'].tolist()

# Read pivot IDs from the input file, if provided
if os.path.exists(input_pivot_file):
    with open(input_pivot_file, 'r') as file:
        input_pivot_ids = [line.strip() for line in file if line.strip()]
        logging.info(f"Loaded {len(input_pivot_ids)} pivot IDs from input file.")
else:
    input_pivot_ids = []
    logging.warning(f"Input pivot file '{input_pivot_file}' not found. Proceeding with all pivots.")

# Combine input pivot IDs with the remaining pivots
pivot_ids = input_pivot_ids + [pivot for pivot in all_pivot_ids if pivot not in input_pivot_ids]

# Iterate over each Landsat collection
for collection_path, (start_year, end_year, landsat_name) in exporter.landsat_collections.items():
    logging.info(f'Starting requests for {landsat_name} collection from {start_year} to {end_year}')
    
    # Attempt to request images
    try:
        exporter.download(
            log_name=log_name,
            pivot_ids=pivot_ids,  
            buffer=True,
            max_cloud_cover=max_cloud_cover,
            completed_pivot_file=completed_pivot_file  
        )
        logging.info(f'Completed requests for {landsat_name} collection')
    except Exception as e:
        logging.error(f'Failed to download images for {landsat_name} collection: {e}')

logging.info('Finished full Landsat image request script')
