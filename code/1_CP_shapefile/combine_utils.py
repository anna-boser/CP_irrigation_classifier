import geopandas as gpd

def calculate_overlap(df1, df2, threshold=0.9):
    """
    Calculate the overlap between two GeoDataFrames.
    """

    df1['area'] = df1.geometry.area
    df2['area'] = df2.geometry.area

    # Perform a spatial join to find intersecting polygons
    joined = gpd.sjoin(df1, df2, how='inner', op='intersects', lsuffix='2000', rsuffix='2021')

    overlaps = []
    for idx, row in joined.iterrows():
        poly1 = df1.loc[idx].geometry # the sjoin keeps the original indices from the first dataset
        poly2 = df2.loc[row['index_2021']].geometry

        # Calculate the intersection and its area
        intersection = poly1.intersection(poly2)
        intersection_area = intersection.area

        # Calculate the overlap percentage
        overlap_percent = intersection_area / min(row.area_2000, row.area_2021)
        if overlap_percent >= threshold:
            overlaps.append((idx, row.index_2021))

    # note: some CPs will be counted as overlapping more than once
    # which is why we will end up with some duplicates in the final gdf and will need to remove them.
    return overlaps 

def create_combined_geodataframe(CPIS2000, CPIS2021, overlaps):
    """
    Create a combined GeoDataFrame from two GeoDataFrames and a list of overlaps.
    """

    combined = []
    seen_2000 = set()
    seen_2021 = set()

    for idx_2000, idx_2021 in overlaps:
        seen_2000.add(idx_2000)
        seen_2021.add(idx_2021)
        combined.append({
            'geometry': CPIS2021.loc[idx_2021].geometry,  # Use 2021 geometry
            'Country': CPIS2021.loc[idx_2021].Country,  # retrieve country name
            'Country Co': CPIS2021.loc[idx_2021]['Country Co'],  
            'year_2000': 1,
            'year_2021': 1,
        })

    # Add remaining polygons from 2000 dataset
    for idx, row in CPIS2000.iterrows():
        if idx not in seen_2000:
            combined.append({
                'geometry': row.geometry,
                'Country': row.Country, # retrieve country name from 2000 dataset
                'Country Co': row['Country Co'],  
                'year_2000': 1,
                'year_2021': 0,
            })

    # Add remaining polygons from 2021 dataset
    for idx, row in CPIS2021.iterrows():
        if idx not in seen_2021:
            combined.append({
                'geometry': row.geometry,
                'Country': row.Country, # retrieve country name from 2021 dataset
                'Country Co': row['Country Co'],  
                'year_2000': 0,
                'year_2021': 1,
            })

    combined_gdf = gpd.GeoDataFrame(combined, columns=['ID', 'year_2000', 'year_2021', 'Country', 'Country Co', 'geometry'], crs=CPIS2000.crs)

    # Remove duplicates caused by CPs being matched to multiple other CPs (eg due to half CPs)
    combined_gdf = combined_gdf.drop_duplicates()

    # Add a unique ID
    combined_gdf['ID'] = range(1, len(combined_gdf) + 1)

    return combined_gdf