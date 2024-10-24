import requests
from bs4 import BeautifulSoup
import pandas as pd

from pdf2image import convert_from_path
from docx import Document
from PIL import Image, ImageDraw, ImageFont
import replicate

from huggingface_hub import InferenceClient
import tempfile
import os
import json
from io import BytesIO
from pathlib import Path
import urllib.parse
from dotenv import load_dotenv

load_dotenv()
hf_token = os.getenv('HUGGINGFACE_TOKEN')
replicate_token = os.getenv('REPLICATE_API_TOKEN')
# Define the directory where images are stored
output_base_dir = "data"

# Web Scraping

def is_valid_pdf(response):
    """Check if the response contains a valid PDF file."""
    content_type = response.headers.get('Content-Type', '')
    return 'application/pdf' in content_type

def create_image_from_text(text, image_path):
    """Create an image from the given text and save it to the specified path."""
    # Create a new blank image
    img = Image.new('RGB', (800, 600), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Optionally, load a custom font
    # font = ImageFont.truetype("arial.ttf", 20)

    # Add text to image
    d.text((10,10), text, fill=(0,0,0))  # Use default font and fill black color
    img.save(image_path)

def scrape_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    table = soup.find("table", class_="tblStandard")  # tblStandard seems to be just the tables we need
    rows = table.find_all("tr")
    
    details = []
    # Create main output directory if it doesn't exist
    os.makedirs(output_base_dir, exist_ok=True)

    for row in rows[1:]:  # Skip the header
        cols = row.find_all("td")
        link = 'https://www.cfm.va.gov' + cols[2].find("a")["href"] if cols[2].find("a") else ""
        
        images = []
        if link:
            pdf_response = requests.get(link, stream=True)
            
            if pdf_response.status_code == 200 and is_valid_pdf(pdf_response):
                # Create a folder for the detail title
                detail_title = cols[1].text.strip().replace('/', '_').replace('\\', '_')  # Clean folder name
                detail_number = cols[0].text.strip()
                # detail_output_dir = os.path.join(output_base_dir, detail_title)
                # os.makedirs(detail_output_dir, exist_ok=True)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    for chunk in pdf_response.iter_content(chunk_size=8192):
                        temp_pdf.write(chunk)
                    temp_pdf_path = temp_pdf.name
                
                try:
                    # Convert the downloaded PDF to images
                    images = convert_from_path(temp_pdf_path)
                        # Save each PIL image permanently
                    for i, img in enumerate(images):
                        if len(detail_number) > 0:
                            file_name = f"{detail_number}_{i + 1}.png"
                            img_path = os.path.join(output_base_dir, file_name)  # Save images as PNGs
                            img.save(img_path, 'PNG')
                        else:
                            print(f"No detail number for {detail_title}")

                        detail = {
                        "file_name": file_name,
                        "number": cols[0].text.strip(),
                        "title": cols[1].text.strip(),
                        "link": img_path
                        }
                        details.append(detail)
                except Exception as e:
                    print(f"Error converting PDF at {link}: {e}")
                
                # Cleanup
                os.remove(temp_pdf_path)
            else:
                print(f"Invalid PDF at {link} or unable to download.")
                 
    
    return pd.DataFrame(details)


def scrape_specifications(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="tblStandard")  # tblStandard seems to be just the tables we need
    rows = table.find_all("tr")
    
    specs = []
    for row in rows[1:]:  # Skip the header
        cols = row.find_all("td")
        link = 'https://www.cfm.va.gov' + cols[0].find("a")["href"] if cols[0].find("a") else ""

        # Download the .docx file if there's a valid link
        if link:
            docx_response = requests.get(link)
            
            if docx_response.status_code == 200:
                # Save the .docx file to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
                    temp_docx.write(docx_response.content)
                    temp_docx_path = temp_docx.name
                
                # Read the .docx file
                doc = Document(temp_docx_path)
                doc_text = '\n'.join([p.text for p in doc.paragraphs if p.text])  # Combine text from paragraphs
                
                # # Create an image from the document text
                # image_path = temp_docx_path.replace('.docx', '.png')  # Save as a PNG file
                # create_image_from_text(doc_text, image_path)

                # Clean up the temporary .docx file
                os.remove(temp_docx_path)

                spec = {
                    "number": cols[0].text.strip(),
                    "title": cols[1].text.strip(),
                    "body": doc_text,
                    "link": link,
                }
                specs.append(spec)
            else:
                print(f"Failed to download .docx file from {link}")
    
    return pd.DataFrame(specs)


construction_details_url = "https://www.cfm.va.gov/til/sdetail.asp"
construction_specs_url = "https://www.cfm.va.gov/til/spec.asp"

details_df = scrape_details(construction_details_url)
specs_df = scrape_specifications(construction_specs_url)

# Before merging, check the structure of details_df
print("Details DataFrame:")
print(details_df.head())
print(details_df.columns)

# Check the specs DataFrame as well
print("Specifications DataFrame:")
print(specs_df.head())
print(specs_df.columns)

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
    'title_body': 'body',
    'link_spec': 'spec_link',
})

final_df = final_df[['file_name', 'detail_number', 'detail_title', 'detail_link', 'spec_number', 'spec_title', 'body', 'spec_link']]

# Display the merged dataframe
print(final_df)

# Data Structuring

# def local_path_to_uri(local_path):
#     # Convert a local file path to a URI
#     local_path = Path(local_path)  # Ensure local path is a Path object
#     absolute_path = local_path.resolve()  # Get the absolute path

#     # Create a URI using file scheme
#     uri = urllib.parse.urljoin('file:', urllib.parse.quote(absolute_path.as_posix()))
#     return uri


# conversational_data = []

# # Process each file in the directory
# for filename in os.listdir(output_base_dir):
#     full_image_path = os.path.join(output_base_dir, filename)

#     # Verify the file is an image
#     if os.path.isfile(full_image_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
#         # Find the corresponding row in the DataFrame
#         matching_rows = final_df[final_df['file_name'] == filename]

#         # If a match is found, process it
#         if not matching_rows.empty:
#             print(matching_rows.columns)
#             for index, row in matching_rows.iterrows():
#                 try:
#                     # # Open image
#                     # image = Image.open(full_image_path).convert("RGB")
#                     image_url = f"https://github.com/simondpalmer/AEC-DETAIL-vision/blob/main/{full_image_path}"
#                     print(image_url)

#                     output = replicate.run(
#                         "yorickvp/llava-13b:80537f9eead1a5bfa72d5ac6ea6414379be41d4d4f6679fd776e9535d1eb58bb",
#                         input={
#                             "image": image_url,
#                             "top_p": 1,
#                             "prompt": f"Can you explain what this {row['detail_title']} drawing indicates? Provide as much detail as possible",
#                             "max_tokens": 2048,
#                             "temperature": 0.0
#                         }
#                     )
#                     result = ''
#                     for item in output:
#                         # https://replicate.com/yorickvp/llava-13b/api#output-schema
#                         result =+ item
                    
#                     print(result)
                    
#                     # Construct data entry
#                     conversation_entry = [
#                             {
#                                 "from": "user",
#                                 "value": f"Can you explain what this {row['detail_title']} drawing indicates? Provide as much detail as possible"
#                             },
#                             {
#                                 "from": "assistant",
#                                 "value": result if result else "No response generated"
#                             }
#                         ]

#                     matching_rows['conversation'] = conversation_entry
#                     matching_rows['image_url'] = image_url

#                 except Exception as e:
#                     print(f"Error processing file {filename}: {e}")

# print(matching_rows.head())
# with open("construction_details_dataset.jsonl", "w") as f:
#     json.dump(matching_rows.to_json(orient='records', lines=True), f, indent=2)


# # Save images permanently
# output_image_dir = "output_images"
# os.makedirs(output_image_dir, exist_ok=True)

# data = []

# # Structuring the conversational data
# for index, row in final_df.iterrows():
#     # Ensure images is a list
#     images = row['images'] if isinstance(row['images'], list) else [row['images']]
    
#     # List to hold file paths for images
#     image_paths = []
    
#     # Save each PIL image permanently
#     for i, img in enumerate(images):
#         img_path = os.path.join(output_image_dir, f"drawing_{index}_{i}.png")
#         img.save(img_path)  # Save the PIL image
#         image_paths.append(img_path)  # Store the path for later use
    
#     # Create conversational entries for each image
#     for image_path in image_paths:
#         data_entry = {
#             "id": f"construction_{index}",
#             "conversations": [
#                 {
#                     "from": "user",
#                     "value": f"Drawing: <img src='https:\\github.com\\simondpalmer\\AEC-DETAIL-vision\\blob\\main\\{image_path}'></img>\nCan you explain what this drawing shows?"
#                 },
#                 {
#                     "from": "assistant",
#                     "value": f"The specification {row['spec_title']} for {row['detail_title']} can be found in the following document: {row['body']}"
#                 }
#             ]
#         }
#         data.append(data_entry)

# with open("construction_dataset.json", "w") as f:
#     json.dump(data, f, indent=2)

# # Publishing Dataset to Hugging Face.
    
# from huggingface_hub import HfApi, HfFolder

# api = HfApi()
# repo_id = "simondavidpalmer/AEC-VA-details-spec-dataset"

# Upload the dataset to the Hugging Face Hub
# api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True, token=hf_token)
# api.upload_file(
#     path_or_fileobj="construction_dataset.json",
#     path_in_repo="construction_dataset.json",
#     repo_id=repo_id,
#     repo_type="dataset"
# )

# print(f"Dataset published at: https://huggingface.co/datasets/{repo_id}")