import os
import re
import numpy as np
import rasterio
import imageio
from PIL import Image
import os
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

class ImageVisualizer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.visualization_names = ["RGB", "NDVI", "LST"]
        self.band_mappings = {
            "Landsat_4_5_7": {"RED": 3, "GREEN": 2, "BLUE": 1, "NIR": 4, "TIR": 6},
            "Landsat_8_9": {"RED": 4, "GREEN": 3, "BLUE": 2, "NIR": 5, "TIR": 10}
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
        if landsat_version in ["Landsat4", "Landsat5", "Landsat7"]:
            return self.band_mappings["Landsat_4_5_7"]
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
        # Extract Landsat version
        landsat_version = self.extract_landsat_version(os.path.basename(tif_file))
        band_mapping = self.get_band_mapping(landsat_version)

        with rasterio.open(tif_file) as src:
            bands = [src.read(i + 1, masked=True).filled(np.nan) for i in range(src.count)]

        base_filename = os.path.splitext(os.path.basename(tif_file))[0]
        for visualization_name in self.visualization_names:
            if visualization_name == "RGB":
                red = self.rescale_to_8bit(bands[band_mapping["RED"] - 1])
                green = self.rescale_to_8bit(bands[band_mapping["GREEN"] - 1])
                blue = self.rescale_to_8bit(bands[band_mapping["BLUE"] - 1])
            elif visualization_name == "NDVI":
                nir = bands[band_mapping["NIR"] - 1]
                red = bands[band_mapping["RED"] - 1]
                ndvi = (nir - red) / (nir + red)
                red = green = blue = self.rescale_to_8bit(ndvi, -1, 1)
            elif visualization_name == "LST":
                lst = bands[band_mapping["TIR"] - 1]
                red = green = blue = self.rescale_to_8bit(lst)
            else:
                continue

            output_file = os.path.join(self.output_dir, f"{base_filename}_{visualization_name}.jpg")
            rgb_image = np.stack((red, green, blue), axis=-1)
            imageio.imsave(output_file, rgb_image, quality=95)

    def create_combined_image(self, base_filename):
        image_files = [os.path.join(self.output_dir, f"{base_filename}_{viz}.jpg") for viz in self.visualization_names]
        images = [Image.open(img) for img in image_files if os.path.exists(img)]
        widths, heights = zip(*(img.size for img in images))
        total_width = sum(widths)
        max_height = max(heights)

        combined_image = Image.new("RGB", (total_width, max_height))
        x_offset = 0
        for img in images:
            combined_image.paste(img, (x_offset, 0))
            x_offset += img.width

        combined_output = os.path.join(self.output_dir, f"{base_filename}_Combined.jpg")
        combined_image.save(combined_output)

    def process_all_images(self):
        tif_files = [
            os.path.join(root, file)
            for root, _, files in os.walk(self.input_dir)
            for file in files if file.lower().endswith(".tif")
        ]

        for tif_file in tif_files:
            base_filename = os.path.splitext(os.path.basename(tif_file))[0]
            self.process_image(tif_file)
            self.create_combined_image(base_filename)


data_root = utils.get_data_root() 
input_dir = os.path.join(data_root, 'intermediate/landsat_training')
output_dir = os.path.join(data_root, '3_labeling/jpeg_images')

visualizer = ImageVisualizer(input_dir, output_dir)
visualizer.process_all_images()
