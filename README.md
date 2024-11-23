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
