

import os
import sys
import geopandas as gpd
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Set the root -- either local or on the server
data_root = utils.get_data_root()

northern_africa_countries = ['Algeria', 'Egypt', 'Libya', 'Morocco', 'Sudan', 'Tunisia', 'Western Sahara']

# Africa = gpd.read_file(data_root + 'raw/Africa_shp/Africa_Boundaries.shp')

# # Filter the Africa shapefile to only include the countries in sub-Saharan Africa
# Africa = Africa[~Africa['Country'].isin(northern_africa_countries)]

# # Save this shapefile
# new_path = data_root + 'intermediate/SSA_shp/'
# if not os.path.exists(new_path):
#     os.makedirs(new_path)
# Africa.to_file(data_root + 'intermediate/SSA_shp/SSA_Boundaries.shp')

# read the combined CPIS shapefile
CPIS = gpd.read_file(data_root + 'intermediate/CPIS/combined_CPIS.shp')

# filter it to only include the countries in sub-Saharan Africa using the country column by checking that it is not in the list of northern African countries
CPIS = CPIS[~CPIS['Country'].isin(northern_africa_countries)]

# Set environment variables for extended timeouts
os.environ["PYDEVD_WARN_EVALUATION_TIMEOUT"] = "10"
os.environ["PYDEVD_UNBLOCK_THREADS_TIMEOUT"] = "10"

# Set PYDEVD_THREAD_DUMP_ON_WARN_EVALUATION_TIMEOUT to true to get a thread dump when a thread evaluation timeout occurs
os.environ["PYDEVD_THREAD_DUMP_ON_WARN_EVALUATION_TIMEOUT"] = "true"

# save this shapefile
cpis_path = data_root + 'intermediate/CPIS/'
if not os.path.exists(cpis_path):
    os.makedirs(cpis_path)
CPIS.to_file(data_root + 'intermediate/CPIS/SSA_CPIS.shp')