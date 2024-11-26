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
pivot_id_file = os.path.join(data_root, '2_data_request/stratified_cp_ids.txt')  # File with 1000 pivot IDs
drive_folder = 'landsat_training_req'
log_name = 'landsat_image_request.log'
max_cloud_cover = 10
images_per_landsat = 200


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


# Iterate over each Landsat collection and request images
for collection_path, (start_year, end_year, landsat_name) in exporter.landsat_collections.items():
    
    # Calculate the number of pivots to use for this collection
    num_pivots = min(images_per_landsat, len(pivot_ids))
    logging.info(f'Requesting {num_pivots} images for {landsat_name}')

    # Iterate over the pivot IDs
    for pivot_id in pivot_ids[:num_pivots]:
        retry_count = 0
        max_retries = 5
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
                years=[random_year],
            )
                logging.info(f'Successfully downloaded image for pivot ID {pivot_id} from {landsat_name} ({random_month}/{random_year})')
                break  # Exit retry loop if successful
            except ValueError as e:  # Specific error when no images are found
                retry_count += 1
                logging.warning(f'Failed to download image for pivot ID {pivot_id} from {landsat_name} ({random_month}/{random_year}): {e}. Retrying ({retry_count}/{max_retries})...')
            except Exception as e:  
                logging.error(f'Unexpected error for pivot ID {pivot_id}: {e}')
                break
    else:
        logging.error(f'Exceeded maximum retries for pivot ID {pivot_id}. Moving to the next pivot.')