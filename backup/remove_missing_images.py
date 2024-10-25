import os
import json
import shutil

# Path to metadata file and image directory
metadata_file = './data/metadata.jsonl'
image_dir = './data'

# Load metadata file into a list of dictionaries
with open(metadata_file, 'r') as f:
    metadata_entries = [json.loads(line) for line in f]

# Create a set of filenames that have metadata
metadata_filenames = {entry['file_name'] for entry in metadata_entries}

# List all image files in the directory
image_files = {file for file in os.listdir(image_dir) if file.lower().endswith(('.png', '.jpg', '.jpeg'))}

# Find images without metadata entries
images_without_metadata = image_files - metadata_filenames

# Report and remove these images
for image in images_without_metadata:
    try:
        # Complete the path to remove the image
        full_image_path = os.path.join(image_dir, image)
        os.remove(full_image_path)
        print(f"Removed image without metadata: {image}")
    except Exception as e:
        print(f"Failed to remove {image}: {e}")

print(f"Cleaned up images without metadata. Remaining images: {len(os.listdir(image_dir))}")