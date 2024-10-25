import pandas as pd

import replicate
from replicate.exceptions import ModelError

import os
import json
from dotenv import load_dotenv

load_dotenv()
# Hugging Face Token
hf_token = os.getenv('HUGGINGFACE_TOKEN')

# Replicate Token
rep_token = os.getenv('REPLICATE_API_TOKEN')

# Define the directory where images are stored
output_base_dir = "data"
output_jsonl_file = os.path.join(output_base_dir, "metadata.jsonl")

details_df= pd.read_pickle("details_df.pkl")
specs_df= pd.read_pickle("specs_df.pkl")

# Process columns to align them for merging
details_df['spec_id'] = details_df['number'].str.extract('(\d{6})')  # Extract the numeric part of the detail number
# Fill NaN values to avoid TypeErrors
details_df['spec_id'] = details_df['spec_id'].fillna('000000')  # Replace NaN with a default value that won’t match any spec

# Reformat to match spec number only if spec_id is valid
details_df['spec_id'] = details_df['spec_id'].apply(
    lambda x: f"{x[:2]} {x[2:4]} {x[4:]}" if x.isdigit() else x
)

# Merge the dataframes on the aligned spec_id and spec number (spec_id is temporary)
merged_df = pd.merge(
    details_df,
    specs_df,
    left_on='spec_id',
    right_on='number',
    suffixes=('_detail', '_spec')
)

# Check the specs DataFrame as well
print("Merged DataFrame:")
print(merged_df.head())
print(merged_df.columns)


# Rename columns to match desired format
final_df = merged_df.rename(columns={
    'file_name' : 'file_name',
    'number_detail': 'detail_number',
    'title_detail': 'detail_title',
    'link_detail': 'detail_link',
    'number_spec': 'spec_number',
    'title_spec': 'spec_title',
    'body': 'spec_body',
    'link_spec': 'spec_link',
})

final_df = final_df[['file_name', 'detail_number', 'detail_title', 'detail_link', 'spec_number', 'spec_title', 'spec_body', 'spec_link']]

# Display the merged dataframe
print(final_df)

# Data Structuring & Infer Image Description

final_df.insert(loc=3, column='detail_description', value=None)

# Helper function to save DataFrame to JSONL
def save_df_to_jsonl(df, filepath):
    """Save DataFrame as a JSON Lines file."""
    with open(filepath, 'w') as f:
        for record in df.to_dict(orient='records'):
            f.write(json.dumps(record) + '\n')

# Process each file in the directory
for file_counter, filename in enumerate(os.listdir(output_base_dir), 1):
    full_image_path = os.path.join(output_base_dir, filename)

    # Verify the file is an image
    if os.path.isfile(full_image_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        # Find the corresponding row in the DataFrame
        matches = final_df['file_name'] == filename
        index_list = final_df.index[matches].tolist()

        if index_list:
            # For each index where the file matches
            for index in index_list:
                image_url = f"https://github.com/simondpalmer/AEC-DETAIL-vision/raw/main/{output_base_dir}/{filename}"
                print("Processing image URL:", image_url)
                
                try:
                    output = replicate.run(
                        "yorickvp/llava-13b:80537f9eead1a5bfa72d5ac6ea6414379be41d4d4f6679fd776e9535d1eb58bb",
                        input={
                            "image": image_url,
                            "top_p": 1,
                            "prompt": f"Can you explain what this {final_df.at[index, 'detail_title']} drawing indicates? Provide as much detail as possible",
                            "max_tokens": 1024,
                            "temperature": 0.1
                        }
                    )

                    result = "".join(output)

                    # Construct description entry
                    image_description = [
                        {
                            "from": "user",
                            "value": f"Can you explain what this {final_df.at[index, 'detail_title']} drawing indicates? Provide as much detail as possible"
                        },
                        {
                            "from": "assistant",
                            "value": result if result else "No response generated"
                        }
                    ]

                    # Update the DataFrame for the specific matched index
                    final_df.at[index, 'detail_description'] = image_description
                    final_df.at[index, 'detail_link'] = image_url

                except Exception as e:
                    print("Failed prediction: " + str(e))
    
    # Periodically save the DataFrame after a certain number of images
    if file_counter % 10 == 0:  # Save every 10 images, adjust as needed
        save_df_to_jsonl(final_df, output_jsonl_file)
        print(f"Periodic save completed after processing {file_counter} files.")

# Final save after all files processed
save_df_to_jsonl(final_df, output_jsonl_file)
print(f"Final DataFrame saved to {output_jsonl_file}")

# Save the DataFrame as a JSON Lines file
output_jsonl_file = os.path.join(output_base_dir, "metadata.jsonl")
final_df.to_json(output_jsonl_file, orient='records', lines=True)
print(f"DataFrame saved to {output_jsonl_file}")
