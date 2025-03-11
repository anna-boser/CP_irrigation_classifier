import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Get the data root using your utils function
data_root = utils.get_data_root()

# Set the input directory to your JPEG folder
input_dir = os.path.join(data_root, 'intermediate/3_labeling/jpeg_training_images')

# Output JSON file path
output_json = os.path.join(data_root, 'intermediate/tasks.json')

# URL of your static server – ensure this matches the server you started
server_url = "http://localhost:8000"

tasks = []
for filename in os.listdir(input_dir):
    # Only include JPEG images that contain "RGB" (case-insensitive)
    if filename.lower().endswith((".jpg", ".jpeg")) and "rgb" in filename.lower():
        # Build the URL by combining the server URL with the filename
        file_url = f"{server_url}/{filename}"
        task = {
            "data": {
                "image": file_url,
                "filename": filename
            }
        }
        tasks.append(task)

with open(output_json, "w") as f:
    json.dump(tasks, f, indent=4)

print(f"Created {output_json} with {len(tasks)} tasks.")

