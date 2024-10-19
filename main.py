import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
from dotenv import load_dotenv

load_dotenv()
hf_token = os.getenv('HUGGINGFACE_TOKEN')

# Web Scraping

def scrape_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    table = soup.find("table", class_="tblStandard")  # tblStandard seems to be just the tables we need
    rows = table.find_all("tr")
    
    details = []
    for row in rows[1:]:  # Skip the header
        cols = row.find_all("td")
        detail = {
            "number": cols[0].text.strip(),
            "title": cols[1].text.strip(),
            "link": 'https://www.cfm.va.gov' + cols[2].find("a")["href"] if cols[2].find("a") else ""
        }
        details.append(detail)
    
    return pd.DataFrame(details)


def scrape_specifications(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="tblStandard")  # tblStandard seems to be just the tables we need
    rows = table.find_all("tr")
    
    specs = []
    for row in rows[1:]:  # Skip the header
        cols = row.find_all("td")
        spec = {
            "number": cols[0].text.strip(),
            "title": cols[1].text.strip(),
            "link": 'https://www.cfm.va.gov' + cols[0].find("a")["href"] if cols[0].find("a") else ""
        }
        specs.append(spec)
    
    return pd.DataFrame(specs)


construction_details_url = "https://www.cfm.va.gov/til/sdetail.asp"
construction_specs_url = "https://www.cfm.va.gov/til/spec.asp"

details_df = scrape_details(construction_details_url)
specs_df = scrape_specifications(construction_specs_url)

print(details_df.head())
print(specs_df.head())

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

# Rename columns to match desired format
final_df = merged_df.rename(columns={
    'number_spec': 'spec_number',
    'title_spec': 'spec_title',
    'link_spec': 'spec_link',
    'number_detail': 'detail_number',
    'title_detail': 'detail_title',
    'link_detail': 'detail_link'
})

final_df = final_df[['spec_number', 'spec_title', 'spec_link', 'detail_number', 'detail_title', 'detail_link']]

# Display the merged dataframe
print(final_df)

# Data Structuring

data = []

# Combining and formatting the scraped data
for index, row in final_df.iterrows():
    data_entry = {
        "id": f"construction_{index}",
        "conversations": [
            {
                "from": "user",
                "value": f"Drawing 1: <img>{row['detail_link']}</img>\nCan you explain what this drawing shows?"
            },
            {
                "from": "assistant",
                "value": f"The specification for {row['detail_title']} can be found in document: {row['spec_link']}"
            }
        ]
    }
    data.append(data_entry)

with open("construction_dataset.json", "w") as f:
    json.dump(data, f, indent=2)

# Publishing Dataset to Hugging Face.
    
# from huggingface_hub import HfApi, HfFolder

# api = HfApi()
# repo_id = "simondavidpalmer/AEC-details-spec-dataset"

# # Upload the dataset to the Hugging Face Hub
# api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True, token=hf_token)
# api.upload_file(
#     path_or_fileobj="construction_dataset.json",
#     path_in_repo="construction_dataset.json",
#     repo_id=repo_id,
#     repo_type="dataset"
# )

# print(f"Dataset published at: https://huggingface.co/datasets/{repo_id}")