import os
import sys
import geopandas as gpd
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Set random seed for reproducibility
random.seed(42)

# Use utils to get data root or handle paths
data_root = utils.get_data_root() 
# Input paths
shapefile_path = os.path.join(data_root, 'intermediate/CPIS/SSA_CPIS.shp')
ssa_geojson_path = os.path.join(data_root, 'raw/map.geojson')

# Output file path
output_txt_file_path = os.path.join(data_root, '2_data_request/stratified_cp_ids.txt')
output_dir = os.path.dirname(output_txt_file_path)
os.makedirs(output_dir, exist_ok=True)

# Read data
original_cp_gdf = gpd.read_file(shapefile_path)
ssa_bbox_gdf = gpd.read_file(ssa_geojson_path)

# Calculate centroids for original shapefile
original_cp_gdf['centroid'] = original_cp_gdf['geometry'].centroid

# Spatial join to get center pivots in Sub-Saharan Africa
center_pivots_in_ssa = gpd.sjoin(original_cp_gdf, ssa_bbox_gdf, predicate='intersects')

# Divide Sub-Saharan Africa into grid cells
grid_size = 1  
center_pivots_in_ssa['grid'] = center_pivots_in_ssa.apply(
    lambda row: (
        int(row.centroid.x / grid_size),
        int(row.centroid.y / grid_size)
    ),
    axis=1
)

# Initialize an empty list to store the IDs of the sampled center pivots
sampled_cp_ids = []

# Maximum number of CPs to admit from the same grid cell
threshold = 4

# Calculate the number of grid cells
unique_grids = center_pivots_in_ssa['grid'].unique()
total_grids = len(unique_grids)

# Calculate the ideal number of samples per grid cell
ideal_samples_per_grid = 1000 // total_grids

# Stratified sampling
for grid_cell in unique_grids:
    # Extract center pivots in the current grid cell
    grid_cell_pivots = center_pivots_in_ssa[center_pivots_in_ssa['grid'] == grid_cell]

    # Define the number of CPs to sample
    sample_size = min(threshold, len(grid_cell_pivots), ideal_samples_per_grid)

    # Sample from the current grid cell
    if sample_size > 0:
        grid_cell_sample = grid_cell_pivots.sample(n=sample_size, random_state=42)
        sampled_cp_ids.extend(grid_cell_sample['ID'])

# If we have fewer than 1000 samples, continue sampling from the largest grid cells
if len(sampled_cp_ids) < 1000:
    remaining_needed = 1000 - len(sampled_cp_ids)
    additional_samples = []

    # Sort grid cells by the number of available pivots
    sorted_grids = sorted(unique_grids, key=lambda g: len(center_pivots_in_ssa[center_pivots_in_ssa['grid'] == g]), reverse=True)

    for grid_cell in sorted_grids:
        if remaining_needed <= 0:
            break
        grid_cell_pivots = center_pivots_in_ssa[center_pivots_in_ssa['grid'] == grid_cell]
        available_pivots = [cp_id for cp_id in grid_cell_pivots['ID'] if cp_id not in sampled_cp_ids]
        additional_sample_size = min(len(available_pivots), remaining_needed)
        if additional_sample_size > 0:
            additional_samples.extend(random.sample(available_pivots, additional_sample_size))
            remaining_needed -= additional_sample_size

    sampled_cp_ids.extend(additional_samples)

# Trim the list to exactly 1000 IDs if it exceeds
sampled_cp_ids = sampled_cp_ids[:1000]

# Write the list of IDs of sampled center pivots to a text file
with open(output_txt_file_path, 'w') as f:
    for cp_id in sampled_cp_ids:
        f.write(str(cp_id) + '\n')

print(f"IDs of sampled center pivots written to {output_txt_file_path}")