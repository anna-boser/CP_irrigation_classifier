# generate a map of the SSA_CPIS shapefile

import geopandas as gpd
import matplotlib.pyplot as plt
import os
import sys
from shapely.geometry import Point
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Set the root -- either local or on the server
data_root = utils.get_data_root()

# read the SSA_CPIS shapefile
CPIS = gpd.read_file(data_root + 'intermediate/CPIS/SSA_CPIS.shp')

# buffer the CPIS points to create a shapefile of the CPIS
CPIS['geometry'] = CPIS.buffer(0.1)

# read the SSA shapefile
SSA = gpd.read_file(data_root + 'intermediate/SSA_shp/SSA_Boundaries.shp')

# plot the shapefile
fig, ax = plt.subplots(figsize=(10, 10))
CPIS.plot(ax=ax, color='blue')
SSA.boundary.plot(ax=ax, color='black')
plt.title('Center Pivot Irrigation Systems in Sub-Saharan Africa')
plt.show()

# save the plot to the output folder using the make_output_path function
output_path = utils.make_output_path('SSA_CPIS_map.png')
fig.savefig(output_path)