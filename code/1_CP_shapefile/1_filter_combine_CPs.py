# This file reads the CPIS shapefiles and the Africa shapefile, and filters the CPIS shapefiles to only include the countries in Africa.

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from combine_utils import calculate_overlap, create_combined_geodataframe
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Set the root -- either local or on the server
data_root = utils.get_data_root()

# Read the shapefiles
CPIS2000 = gpd.read_file(data_root + 'raw/CPIS/World_CPIS_2000.shp')
CPIS2021 = gpd.read_file(data_root + 'raw/CPIS/World_CPIS_2021.shp')
Africa = gpd.read_file(data_root + 'raw/Africa_shp/Africa_Boundaries.shp')

# Filter the Africa shapefile to only include the countries in sub-Saharan Africa
northern_africa_countries = ['Algeria', 'Egypt', 'Libya', 'Morocco', 'Sudan', 'Tunisia', 'Western Sahara']
Africa = Africa[~Africa['Country'].isin(northern_africa_countries)]

# Save this shapefile
new_path = data_root + 'intermediate/SSA_shp/'
if not os.path.exists(new_path):
    os.makedirs(new_path)
Africa.to_file(data_root + 'intermediate/SSA_shp/SSA_Boundaries.shp')

# Perform the spatial intersection
CPIS2000 = gpd.overlay(CPIS2000, Africa, how='intersection')
CPIS2021 = gpd.overlay(CPIS2021, Africa, how='intersection')

# Add a 'year' column to each dataframe
CPIS2000['Year'] = 2000
CPIS2021['Year'] = 2021

# Get the indices of the overlapping polygons
overlaps = calculate_overlap(CPIS2000, CPIS2021, threshold=0.9)

# Create combined geodataframe
combined_gdf = create_combined_geodataframe(CPIS2000, CPIS2021, overlaps)

# Save the combined geodataframe
combined_gdf.to_file(data_root + 'intermediate/CPIS/SSA_CPIS.shp')