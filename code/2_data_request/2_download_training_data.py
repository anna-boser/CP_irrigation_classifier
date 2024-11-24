import logging
import random
from exporter_class import LandsatDataExporter  
import utils

'''Using the LandsatDataExporter class we are going to request training data for labeling,
within this script you will provide the shp file obtained from '2_filter_to_SSA.py.
You will also provide the # of images you want to request per landsat, since we are shuffling
the list of our pivot ID's, we can request # images per landsat recursively and obtain a random
sample with an even distribution
'''
# Provide file and image count info
data_root = utils.get_data_root()
shapefile_path = data_root + 'intermediate/CPIS/SSA_CPIS.shp'
drive_folder = 'landsat_training_request'
log_name = 'landsat_image_request.log'
max_cloud_cover = 10
images_per_landsat = 200

# Setup logging
logging.basicConfig(filename=log_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Initialize the LandsatDataExporter
exporter = LandsatDataExporter(shapefile_path, drive_folder)
logging.info('Initialized LandsatDataExporter')

# Convert Pivot ID's to a list
pivot_ids = exporter.center_pivot_gdf['Id'].tolist()
random.shuffle(pivot_ids)  # Shuffle to get a random sample


# Iterate over each Landsat collection and request 200 random images
for collection_path, (start_year, end_year, landsat_name) in exporter.landsat_collections.items():
    logging.info(f'Starting requests for {landsat_name} collection from {start_year} to {end_year}')
    
    # Calculate the number of pivots to use for this collection
    num_pivots = min(images_per_landsat, len(pivot_ids))
    logging.info(f'Requesting {num_pivots} images for {landsat_name}')

    # Attempt to request images
    try:
        exporter.download(
            log_name=log_name,
            pivot_ids=pivot_ids[:num_pivots],  # Limit to the number of images per Landsat
            buffer=True,
            max_cloud_cover=max_cloud_cover,
            landsats=[landsat_name] * num_pivots,  
            months=[random.randint(1, 12) for _ in range(num_pivots)],  # Random months
            years=[random.randint(start_year, end_year) for _ in range(num_pivots)]  # Random years within the collection's range
        )
        logging.info(f'Completed requests for {landsat_name} collection')
    except Exception as e:
        logging.error(f'Failed to download images for {landsat_name} collection: {e}')

logging.info('Finished Landsat image requests')