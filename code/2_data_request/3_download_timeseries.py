import logging
from exporter_class import LandsatDataExporter 
import os
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

'''To obtain data for our timeseries we will use this script to call LandsatDataExporter
request all available images across all 5 landsats for each center pivot. Due to the large
# of data we are requesting we also call our download function with a 'completed_pivot_file'
parameter. Within our download function we have methods to write in the ID of every pivot
we request into a text file, if provided when calling the function this text file will provide
the ID's of previously requested pivots, allowing us to continue progress if the script 
stops execution before the requests are finished.
'''
# Initialize parameters
data_root = utils.get_data_root()
shapefile_path = data_root + 'intermediate/CPIS/SSA_CPIS.shp'
drive_folder = 'landsat_timeseries_request'
log_name = 'landsat_full_request.log'
completed_pivot_file = 'completed_pivots.txt'
max_cloud_cover = 100  # Set to 100 to ensure no images are missed

# Setup logging
logging.basicConfig(filename=log_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Initialize the exporter
exporter = LandsatDataExporter(shapefile_path, drive_folder)
logging.info('Initialized LandsatDataExporter')

# Generate a list of pivot IDs
pivot_ids = exporter.center_pivot_gdf['Id'].tolist()


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