# CP_irrigation_classifier
This repository is used to train and deploy an algorithm capable of sensing whether land in sub-Saharan Africa is irrigated or not. 

## Setup
The code in this directory is written in Python, and we use anaconda and a requirements.txt to manage our packages. Download anaconda and run the following commands in your terminal to set up your environment: 

```{bash}
conda create -n cp_pipeline python=3.9 -y
conda activate cp_pipeline
pip install -r requirements.txt
```

## Shapefile containing Center Pivots across the World

You can obtain the shp file containing the world's center pivots [here](https://github.com/DetectCPIS/global_cpis_shp). 

To extract the Center Pivots identified in 2021, download all files in [this folder](https://github.com/DetectCPIS/global_cpis_shp/tree/main/World_CPIS_2021) and run the following code in the terminal: 

```{bash}
cd ~/Downloads 
zip -s 0 World_CPIS_2021.zip --out World_CPIS_2021_together.zip
unzip World_CPIS_2021_together.zip
```
## Data inventory

A list of all data used and created in this project can be found under `data.txt`. This file reflects all data that can be found in the waves/data/CP_irrigation_classifier/data folder on the ERI cluster, and the same structure should be maintained for files also kept locally. 

## Instructions

1. Download all raw data files listed in the data inventory, either from their original source or the waves repository.
2. Run all code in order. 

## Pipeline Overview
The pipline is structured around 6 main tasks listed in  the `code` folder to prepare and train our model to sense whether land in Sub-Saharan Africa is irrigated:
    1. Obtain a shapefile containing all known center pivot locations in Sub-Saharan Africa, `code/1_CP_Shapefile`. (Python)
    2. Download TIF imagery from Landsats 5, 7, 8, and 9 for model training and application, `code/2_data_request`. (Python, Google Earth Engine, Google Drive)
    3. Creating visual images from Landsat data to create annotations/labels used in training, `code/3_labeling`. (Python, Label Studio)
        - In depth analysis on labeling can be found in the `labeling.txt` text file
    4. Using label annotations to create datasets for training and testing model performance, `code/4_data_pipeline`. (Python)
    5. Training model performance using methods of cross-validation, `code/5_model_training`. (Python)
    6. Applying model to all Landsat imagery for known center pivot locations to obtain a time series of center pivot usage, `code/6_time_series`. (Python)
        - TIF imagery from Landsats 5, 7, 8 and 9 only.
In addition to the code listed in the filepaths above, the `code` folder also includes Python Scripts aimed to assist with the pipeline process. These include:
    1. `utils.py` - Obtains root directory path, allowing scripts to run locally and on the ERI Cluster
    2. `check_tasks.py` - Check the # of tasks uploaded to Google Earth Engine
    3. `task_canceller.py` - Eliminate execution all currently running/queued tasks in Google Earth Engine

### **Obtaining Shapefile of Center Pivots in Sub-Saharan Africa**
This section describes how to use the pipeline in the `code/1_CP_Shapefile` directory to filter, combine, and map center pivots (CPs) in Sub-Saharan Africa (SSA).

#### **Step 1: Filter and Combine Center Pivot Data**
**Script**: `1_filter_combine_CPs.py`  
**Utilities**: `combine_utils.py`  
**Purpose**: This script reads the global CPIS shapefiles for 2000 and 2021 and filters them to include only African countries. It uses utility functions from `combine_utils.py` to detect overlapping CPs and creates a combined shapefile.  

- **Input Files**:
  - Global CPIS shapefiles for 2000 and 2021 (`World_CPIS_2000.shp` and `World_CPIS_2021.shp`).
  - Africa boundary shapefile (`Africa_Boundaries.shp`).

- **Key Functions**:
  1. Filters CPs to include only those in Africa using a spatial intersection with `Africa_Boundaries.shp`.
  2. Uses the `calculate_overlap` function from `combine_utils.py` to detect overlapping CPs (90% overlap threshold).
  3. Combines the filtered datasets and assigns a unique ID to each pivot.

- **Output**:
  - Combined shapefile: `combined_CPIS.shp` saved in the `intermediate/CPIS` directory.

#### **Step 2: Filter CPs to Sub-Saharan Africa**
**Script**: `2_filter_to_SSA.py`  
**Purpose**: Filters the combined CPIS shapefile to retain only CPs located in Sub-Saharan Africa (SSA).  

- **Input Files**:
  - Combined CPIS shapefile: `combined_CPIS.shp`.
  - List of Northern African countries (excluded from SSA):
    - Algeria, Egypt, Libya, Morocco, Sudan, Tunisia, Western Sahara.

- **Key Functions**:
  1. Excludes CPs located in Northern African countries based on the `Country` field.
  2. Saves the filtered shapefile as `SSA_CPIS.shp`.

- **Output**:
  - Filtered shapefile: `SSA_CPIS.shp` containing only CPs in SSA.

#### **Step 3: Map Center Pivots in SSA**
**Script**: `3_map_CPIS.py`  
**Purpose**: Generates a visual map of CP locations in SSA.  

- **Input Files**:
  - Sub-Saharan CPIS shapefile: `SSA_CPIS.shp`.
  - SSA boundaries shapefile: `SSA_Boundaries.shp`.

- **Key Functions**:
  1. Buffers the CP points slightly for improved visualization.
  2. Plots the CPs against SSA boundaries using `matplotlib`.
  3. Saves the map as an image (`SSA_CPIS_map.png`) in the `output` folder.

- **Output**:
  - Visual map of SSA CP locations: `SSA_CPIS_map.png`.

#### **Utilities: combine_utils.py**
This utility script contains reusable functions for spatial operations, such as:
- **`calculate_overlap`**:
  - Detects overlapping pivots based on their geometry and an overlap threshold (default: 90%).
- **`get_centroid`**:
  - Computes the centroids of geometries for point-based operations.

`combine_utils.py` is imported and used by `1_filter_combine_CPs.py` for key spatial operations.

#### **Usage Instructions**
To obtain the shapefile for Sub-Saharan Africa:
1. Run `1_filter_combine_CPs.py` to filter and combine CPIS data for Africa.
2. Run `2_filter_to_SSA.py` to extract CPs specifically for SSA.
3. Run `3_map_CPIS.py` to visualize the filtered CP data in SSA.

Ensure that the required input files are placed in the correct `raw` directory before running the scripts. Each script will output intermediate or final results into the appropriate directories.

### **Downloading TIF Imagery for Training Data**
This section describes how to use the pipeline in the `code/2_data_request` directory to download TIF imagery from Landsats 5, 7, 8, and 9 for model training purposes.

#### **Step 1: Stratified Sampling of Center Pivots**
**Script**: `1_stratified_filter_cp.py`  
**Purpose**: Selects a stratified random sample of 1,000 center pivots across Sub-Saharan Africa for training data requests.  

- **Input Files**:
  - Sub-Saharan CPIS shapefile: `SSA_CPIS.shp`.
  - GeoJSON boundary of SSA: `map.geojson`.

- **Key Functions**:
  1. Computes centroids of all CP geometries in SSA.
  2. Divides SSA into grid cells and assigns CPs to grid cells based on their centroid.
  3. Samples CPs within each grid cell, ensuring no more than 4 CPs per cell and balancing across grids.
  4. Writes the sampled CP IDs to a text file for downstream use.

- **Output**:
  - Stratified CP ID text file: `stratified_cp_ids.txt`.

#### **Step 2: Downloading Training Data**
**Script**: `2_download_training_data.py`  
**Utilities**: `exporter_class.py`  
**Purpose**: Downloads TIF imagery for the stratified CP sample across Landsats 5, 7, 8, and 9. The downloaded imagery is saved to a Google Drive folder for labeling.

- **Input Files**:
  - Stratified CP ID text file: `stratified_cp_ids.txt`.
  - Sub-Saharan CPIS shapefile: `SSA_CPIS.shp`.

- **Key Functions**:
  1. Reads the CP IDs from the stratified sample.
  2. Initializes the `LandsatDataExporter` class from `exporter_class.py`.
  3. Downloads TIF imagery for up to 250 CPs per Landsat collection (Landsat 5, 7, 8, and 9), using random years and months to ensure diversity in the imagery.
  4. Logs all download activities to `training_data_request.log`.

- **Output**:
  - Downloaded TIF imagery saved to a Google Drive folder: `training_data_C02`.
  - Log file: `training_data_request.log`.

#### **Step 3: Downloading Full Time Series**
**Script**: `3_download_timeseries.py`  
**Utilities**: `exporter_class.py`  
**Purpose**: Downloads the full time series of TIF imagery for all known CPs in SSA.  

- **Input Files**:
  - Sub-Saharan CPIS shapefile: `SSA_CPIS.shp`.

- **Key Functions**:
  1. Reads all CP IDs from the shapefile.
  2. Uses `exporter_class.py` to iterate through all Landsat collections.
  3. Requests images for each CP across all available years for Landsats 5, 7, 8, and 9.
  4. Handles partial downloads by tracking completed CPs in `completed_pivots.txt`.

- **Output**:
  - Full time series TIF imagery saved to a Google Drive folder: `landsat_timeseries_request`.
  - Log file: `landsat_full_request.log`.

#### **Utilities: exporter_class.py**
This utility script contains the `LandsatDataExporter` class, which handles TIF imagery requests and preprocessing tasks:
- **`download`**:
  - Downloads TIF imagery to Google Drive for specified CPs, Landsat collections, and time ranges.
  - Applies QA masking and scales the images based on Landsat Collection 2 recommendations.
- **`apply_scale_factors`**:
  - Applies scaling factors to Landsat reflectance and thermal bands.
- **`qa_mask`**:
  - Masks poor-quality pixels based on the QA bitmask.

#### **Usage Instructions**
To download training data:
1. Run `1_stratified_filter_cp.py` to generate the stratified CP ID text file.
2. Run `2_download_training_data.py` to request TIF imagery for training.
3. Run `3_download_timeseries.py` to download the full time series for all CPs. (Can be done after model is trained)

### **Creating Visuals for Labeling**
This step focuses on creating and visualizing labeled images to support the annotation process for training the irrigation classifier. The pipeline allows for generating JPEG images of center pivots and interactively viewing these images for annotations.

---

#### **Step 1: Generate JPEG Visualizations**
**Script**: `image_creator.py`  
**Purpose**: Processes TIF images to generate JPEG visualizations for labeling. The visualizations include:
- **RGB images**: Created using bands representing red, green, and blue reflectance.
- **Combined images**: Merges RGB, NDVI, and LST into a single visualization.

**Key Functions**:
1. Reads TIF files from the `training_data_C02` directory.
2. For each TIF file:
   - Extracts the Landsat version from the filename (e.g., Landsat 5, 7, 8, or 9).
   - Creates an RGB image by rescaling the red, green, and blue bands to 8-bit.
   - Computes NDVI and LST values, rescaling them for visualization.
   - Combines RGB, NDVI, and LST into a side-by-side image.
3. Saves the visualizations (RGB and Combined) as JPEGs in the `jpeg_training_images` directory.

**Input Files**:
- TIF imagery: Found in `intermediate/2_data_request/training_data_C02`.

**Output**:
- RGB and Combined JPEG images: Saved to `intermediate/3_labeling/jpeg_training_images`.

---

#### **Utililties: Analyze LST Values**
**Script**: `lst_value_checker.py`  
**Purpose**: Analyzes preprocessed Landsat 9 TIF images to ensure the thermal (LST) band values are within expected ranges.  
This script is primarily used for debugging to identify issues with scaling or quality in the LST band.

**Key Functions**:
1. Iterates over all Landsat 9 TIF files in the `training_data_C02` directory.
2. Extracts the thermal band (`ST_B10`) and calculates:
   - Minimum, maximum, and mean values.
   - Count of valid (non-NaN) and invalid (NaN) pixels.
3. Flags files with:
   - Unusual value ranges (e.g., min < 200 K or max > 400 K).
   - Low valid pixel counts (less than 50% valid).

**Input Files**:
- Landsat 9 TIF imagery: Found in `intermediate/2_data_request/training_data_C02`.

**Output**:
- Summary of thermal band statistics printed to the console with warnings for outliers or issues.

---

#### **Utilities 2: Interactive TIF Visualization**
**Script**: `tif_visualizer_notebook.ipynb`  
**Purpose**: Allows users to interactively view TIF files one pivot at a time. The notebook supports:
- Filtering by Landsat collection (5, 7, 8, or 9).
- Searching for specific pivots using their ID.
- Generating RGB, NDVI, and LST visualizations for quick annotation review.

**Key Functions**:
- Interactive widgets:
  - Dropdown menu to filter by Landsat collection.
  - Text search for specific pivot IDs.
- Generates side-by-side combined visualizations of RGB, NDVI, and LST.

**Input Files**:
- TIF imagery: Found in `intermediate/2_data_request/training_data_C02`.

**Output**:
- Visualization displayed in the notebook.

**Notes**:  
The notebook is primarily for the labeling process. Detailed instructions on labeling will be provided in the `labeling.txt` file in the `3_labeling` directory.

---

#### **Usage Instructions**
Follow the steps listed in `labeling.txt` to ensure accurate labeling.

Ensure that input files are located in the correct directories (`intermediate/2_data_request/training_data_C02`) and that the outputs are reviewed for quality.


