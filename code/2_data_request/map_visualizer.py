import os
import sys
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

data_root = utils.get_data_root()

# Paths to input files:
ssacpis_path = os.path.join(data_root, 'intermediate', 'CPIS', 'SSA_CPIS.shp')
stratified_ids_path = os.path.join(data_root, 'intermediate', '2_data_request', 'stratified_cp_ids.txt')
ssa_boundary_geojson = os.path.join(data_root, 'raw', 'map.geojson')

# Load the SSA_CPIS shapefile
ssacpis_gdf = gpd.read_file(ssacpis_path)

# Load the stratified pivot IDs
with open(stratified_ids_path, 'r') as f:
    stratified_ids = set(line.strip() for line in f if line.strip())

# Filter SSA_CPIS to only include pivots that were sampled
sampled_gdf = ssacpis_gdf[ssacpis_gdf['ID'].astype(str).isin(stratified_ids)].copy()

# Calculate centroids and assign grid cell coordinates (grid_size = 1 unit)
grid_size = 1
sampled_gdf['centroid'] = sampled_gdf['geometry'].centroid
sampled_gdf['grid'] = sampled_gdf.apply(lambda row: (int(row.centroid.x / grid_size), int(row.centroid.y / grid_size)), axis=1)

# Determine unique grids and print the count
unique_grids = sampled_gdf['grid'].unique()
print(f"Total number of grid cells: {len(unique_grids)}")

# Group by grid cell and count number of pivots in each cell
grid_counts = sampled_gdf.groupby('grid').size().reset_index(name='sample_count')

# Create a GeoDataFrame for grid cells using the grid key
def create_grid_cell_geometry(grid_key, grid_size=1):
    gx, gy = grid_key
    return box(gx * grid_size, gy * grid_size, (gx + 1) * grid_size, (gy + 1) * grid_size)

grid_counts['geometry'] = grid_counts['grid'].apply(create_grid_cell_geometry)
grid_gdf = gpd.GeoDataFrame(grid_counts, geometry='geometry', crs=sampled_gdf.crs)

# Load the SSA boundary from map.geojson
ssa_boundary = gpd.read_file(ssa_boundary_geojson)

# Print total number of pivot IDs loaded from the txt file
print(f"Total number of pivot IDs from stratified_cp_ids.txt: {len(stratified_ids)}")

# Plot the results with adjusted normalization for the heatmap
fig, ax = plt.subplots(figsize=(12, 12))
ssa_boundary.boundary.plot(ax=ax, color='black', linewidth=1)
# Adjust heatmap normalization: set vmin=0 and vmax=50 to enhance color variation
grid_gdf.plot(ax=ax, column='sample_count', cmap='OrRd', legend=True, alpha=0.6, edgecolor='grey', vmin=0, vmax=5)
sampled_gdf.plot(ax=ax, color='blue', markersize=5, label='Sampled Pivots')
plt.title('Stratified Grid Sample Counts for SSA Center Pivots')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend()

output_map = os.path.join(data_root, 'intermediate', '4_data_pipeline', 'SSA_grid_samples.png')
plt.savefig(output_map, dpi=300, bbox_inches='tight')
plt.show()

print(f"Grid sample map saved to: {output_map}")
