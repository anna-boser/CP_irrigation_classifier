import logging
import random
from exporter_class import LandsatDataExporter
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils


'''Using the LandsatDataExporter class, we are going to request training data for labeling,
   Within this script, you will provide the shp file obtained from '2_filter_to_SSA.py'.
   The pivot IDs are now provided via a text file containing 1000 IDs.
'''

# Provide file and image count info
data_root = utils.get_data_root()
shapefile_path = os.path.join(data_root, 'intermediate/CPIS/SSA_CPIS.shp')
pivot_id_file = os.path.join(data_root, 'intermediate/2_data_request/stratified_cp_ids.txt')  # File with 1000 pivot IDs
drive_folder = 'training_data_C02'
log_name = 'training_data_request.log'
max_cloud_cover = 10
images_per_landsat = 250

# Setup logging
logging.basicConfig(filename=log_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the pivot IDs from the text file
try:
    with open(pivot_id_file, 'r') as f:
        pivot_ids = [line.strip() for line in f.readlines()]
    logging.info(f'Loaded {len(pivot_ids)} pivot IDs from {pivot_id_file}')
except Exception as e:
    logging.error(f'Failed to load pivot IDs from {pivot_id_file}: {e}')
    sys.exit(1)

# Initialize the LandsatDataExporter
exporter = LandsatDataExporter(shapefile_path, drive_folder)

# Track processed pivots to avoid duplicates across collections
processed_pivots = set()

start_index = 0  # Tracks the start index for each Landsat collection

for collection_path, (start_year, end_year, landsat_name) in exporter.landsat_collections.items():
    # Calculate the number of pivots to use for this collection
    num_pivots = min(images_per_landsat, len(pivot_ids) - start_index)  # Adjust for remaining pivots
    pivot_subset = pivot_ids[start_index:start_index + num_pivots]  # Subset for this collection
    start_index += num_pivots  # Shift start index for the next collection

    logging.info(f'Requesting up to {num_pivots} images for {landsat_name}')

    # Iterate over the subset of pivot IDs
    for pivot_id in pivot_subset:
        if pivot_id in processed_pivots:
            logging.info(f"Skipping pivot ID {pivot_id} as it has already been processed.")
            continue

        retry_count = 0
        max_retries = 15
        success = False

        while retry_count < max_retries:
            try:
                random_year = random.randint(start_year, end_year)
                random_month = random.randint(1, 12)
                
                # Call the download function
                exporter.download(
                    log_name=log_name,
                    pivot_ids=[pivot_id],
                    buffer=True,
                    max_cloud_cover=max_cloud_cover,
                    landsats=[landsat_name],
                    months=[random_month],
                    years=[random_year]
                )
                logging.info(f'Successfully downloaded image for pivot ID {pivot_id} from {landsat_name} ({random_month}/{random_year})')
                processed_pivots.add(pivot_id)  # Mark pivot as processed
                success = True
                break  # Exit retry loop if successful
            except ValueError as e:  # Specific error when no images are found
                retry_count += 1
                logging.warning(f'Failed to download image for pivot ID {pivot_id} from {landsat_name} ({random_month}/{random_year}): {e}. Retrying ({retry_count}/{max_retries})...')
            except Exception as e:
                logging.error(f'Unexpected error for pivot ID {pivot_id}: {e}')
                break
        if not success:
            logging.error(f'Exceeded maximum retries for pivot ID {pivot_id}. Moving to the next pivot.')

logging.info(f'Finished requesting training data for up to {len(processed_pivots)} unique pivot IDs from {pivot_id_file}')
