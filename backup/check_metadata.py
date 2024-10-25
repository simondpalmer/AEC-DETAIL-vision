import os
import pandas as pd
import json

# Load metadata
metadata_file = './data/metadata.jsonl'
with open(metadata_file, 'r') as f:
    metadata_entries = [json.loads(line) for line in f]

# Ensure file_name is accurate and matches the image filenames
metadata_df = pd.DataFrame(metadata_entries)
print("Metadata loaded and converted to DataFrame.")

# Directory where images are stored
image_dir = './data'

# List all images in the directory
image_files = {file for file in os.listdir(image_dir) if file.lower().endswith(('.png', '.jpg', '.jpeg'))}

# Check for missing metadata entries
missing_metadata = image_files - set(metadata_df['file_name'])

if missing_metadata:
    print("Images missing from metadata:", missing_metadata)