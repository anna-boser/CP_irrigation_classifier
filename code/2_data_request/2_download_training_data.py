import logging
import random
from exporter_class import LandsatDataExporter
import utils
import os
import sys

# Add the parent directory to the module search path to locate utils.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

'''Using the LandsatDataExporter class, we are going to request training data for labeling,
   Within this script, you will provide the shp file obtained from '2_filter_to_SSA.py'.
   The pivot IDs are now provided via a text file containing 1000 IDs.
'''

# Provide file and image count info
data_root = utils.get_data_root()
shapefile_path = os.path.join(data_root, 'intermediate/CPIS/SSA_CPIS.shp')
pivot_id_file = os.path.join(data_root, '2_data_request/stratified_cp_ids.txt')  # File with 1000 pivot IDs
drive_folder = 'landsat_training_request'
log_name = 'landsat_image_request.log'
completed_pivot_file = 'completed_pivots.txt'
max_cloud_cover = 10
images_per_landsat = 200
max_retries = 5  # Maximum number of retries per image

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
logging.info('Initialized LandsatDataExporter')

# Iterate over each Landsat collection and request images
for collection_path, (start_year, end_year, landsat_name) in exporter.landsat_collections.items():
    logging.info(f'Starting requests for {landsat_name} collection from {start_year} to {end_year}')
    
    # Calculate the number of pivots to use for this collection
    num_pivots = min(images_per_landsat, len(pivot_ids))
    logging.info(f'Requesting {num_pivots} images for {landsat_name}')

    # Iterate over the pivot IDs
    for pivot_id in pivot_ids[:num_pivots]:
        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            try:
                # Generate a random date for this Landsat collection
                random_month = random.randint(1, 13)
                random_year = random.randint(start_year, end_year)

                # Attempt to request an image for the current pivot ID
                exporter.download(
                    log_name=log_name,
                    pivot_ids=[pivot_id],  # Single pivot ID for this request
                    buffer=True,
                    max_cloud_cover=max_cloud_cover,
                    landsats=[landsat_name],
                    months=[random_month],
                    years=[random_year],
                    completed_pivot_file=completed_pivot_file 
                )
                
                logging.info(f'Successfully downloaded image for pivot ID {pivot_id} from {landsat_name} ({random_month}/{random_year})')
                success = True  # Exit the retry loop after success
            except Exception as e:
                retry_count += 1
                logging.warning(f'Failed to download image for pivot ID {pivot_id} from {landsat_name} ({random_month}/{random_year}): {e}')
                if retry_count < max_retries:
                    logging.info(f'Retrying for pivot ID {pivot_id} ({retry_count}/{max_retries})')

        if not success:
            logging.error(f'Exceeded maximum retries for pivot ID {pivot_id}. Moving to the next pivot.')

logging.info('Finished Landsat image requests')
