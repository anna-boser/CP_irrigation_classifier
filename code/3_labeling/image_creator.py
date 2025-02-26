import os
import re
import numpy as np
import rasterio
import imageio
from PIL import Image
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

class ImageVisualizer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.visualization_names = ["RGB", "Combined"]  # Only RGB and Combined outputs
        self.band_mappings = {
            "Landsat_5_7": {"RED": 3, "GREEN": 2, "BLUE": 1, "NIR": 4, "TIR": 6},
            "Landsat_8_9": {"RED": 4, "GREEN": 3, "BLUE": 2, "NIR": 5, "TIR": 9}
        }

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def rescale_to_8bit(self, band_array, min_value=None, max_value=None):
        valid_pixels = band_array[~np.isnan(band_array)]
        if len(valid_pixels) == 0:
            min_value, max_value = 0, 255
        else:
            if min_value is None:
                min_value = np.percentile(valid_pixels, 2)
            if max_value is None:
                max_value = np.percentile(valid_pixels, 98)

        band_array = np.clip(band_array, min_value, max_value)
        band_array = ((band_array - min_value) / (max_value - min_value) * 255).astype(np.uint8)
        return np.nan_to_num(band_array)

    def get_band_mapping(self, landsat_version):
        if landsat_version in ["Landsat5", "Landsat7"]:
            return self.band_mappings["Landsat_5_7"]
        elif landsat_version in ["Landsat8", "Landsat9"]:
            return self.band_mappings["Landsat_8_9"]
        else:
            raise ValueError(f"Unsupported Landsat version: {landsat_version}")

    def extract_landsat_version(self, filename):
        # Extract Landsat version from the filename using regex
        match = re.search(r"Landsat\d+", filename)
        if match:
            return match.group(0)
        else:
            raise ValueError(f"Landsat version could not be determined from filename: {filename}")

    def process_image(self, tif_file):
        """Generate and save RGB and NDVI visualizations for a single TIF file."""
        # Extract Landsat version
        landsat_version = self.extract_landsat_version(os.path.basename(tif_file))
        band_mapping = self.get_band_mapping(landsat_version)

        with rasterio.open(tif_file) as src:
            bands = [src.read(i + 1, masked=True).filled(np.nan) for i in range(src.count)]

        # Generate RGB visualization
        red = self.rescale_to_8bit(bands[band_mapping["RED"] - 1])
        green = self.rescale_to_8bit(bands[band_mapping["GREEN"] - 1])
        blue = self.rescale_to_8bit(bands[band_mapping["BLUE"] - 1])
        rgb_image = np.stack((red, green, blue), axis=-1)

        # Save RGB image
        base_filename = os.path.splitext(os.path.basename(tif_file))[0]
        rgb_output_file = os.path.join(self.output_dir, f"{base_filename}_RGB.jpg")
        imageio.imsave(rgb_output_file, rgb_image, quality=95)

        # Generate Combined visualization
        nir = bands[band_mapping["NIR"] - 1]
        ndvi = (nir - red) / (nir + red)
        ndvi_image = self.rescale_to_8bit(ndvi, -1, 1)

        lst = bands[band_mapping["TIR"] - 1]
        lst_image = self.rescale_to_8bit(lst)

        combined_output = self.create_combined_image(base_filename, rgb_image, ndvi_image, lst_image)
        return combined_output

    def create_combined_image(self, base_filename, rgb_image, ndvi_image, lst_image):
        """Combine RGB, NDVI, and LST images side by side and save."""
        # Stack images horizontally
        combined_image = np.hstack((rgb_image, np.stack((ndvi_image,) * 3, axis=-1), np.stack((lst_image,) * 3, axis=-1)))

        # Save combined image
        combined_output = os.path.join(self.output_dir, f"{base_filename}_Combined.jpg")
        imageio.imsave(combined_output, combined_image, quality=95)

        return combined_output

    def process_all_images(self):
        """Process all TIF files in the input directory."""
        tif_files = [
            os.path.join(root, file)
            for root, _, files in os.walk(self.input_dir)
            for file in files if file.lower().endswith(".tif")
        ]

        for tif_file in tif_files:
            try:
                print(f"Processing: {tif_file}")
                self.process_image(tif_file)
            except Exception as e:
                print(f"Error processing {tif_file}: {e}")


# Set up directories
data_root = utils.get_data_root() 
input_dir = os.path.join(data_root, 'intermediate/training_data_C02')
output_dir = os.path.join(data_root, 'intermediate/3_labeling/jpeg_training_images')

# Initialize visualizer and process images
visualizer = ImageVisualizer(input_dir, output_dir)
visualizer.process_all_images()
