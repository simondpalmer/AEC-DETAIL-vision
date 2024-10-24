import requests
from bs4 import BeautifulSoup
import pandas as pd
from pdf2image import convert_from_path
from docx import Document
from urllib.parse import urljoin
import tempfile
import os

from dotenv import load_dotenv

load_dotenv()
hf_token = os.getenv('HUGGINGFACE_TOKEN')
os.environ["REPLICATE_API_TOKEN"] = os.getenv('REPLICATE_API_TOKEN')

# Define the directory where images are stored
output_base_dir = "data"

# Web Scraping

def is_valid_pdf(response):
    """Check if the response contains a valid PDF file."""
    content_type = response.headers.get('Content-Type', '')
    return 'application/pdf' in content_type

def scrape_details(url):
    # Create main output directory if it doesn't exist
    os.makedirs(output_base_dir, exist_ok=True)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser") 
    details = []

    tables = soup.find_all("table", class_="tblStandard")  # tblStandard seems to be just the tables we need
    
    for table in tables:
        rows = table.find_all("tr")
        
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
    specs = []

    tables = soup.find_all("table", class_="tblStandard")  # tblStandard seems to be just the tables we need
    
    for table in tables:
        rows = table.find_all("tr")

        for row in rows[1:]:  # Skip the header
            cols = row.find_all("td")

            # Safely construct the full URL
            link_tag = cols[0].find("a")
            if link_tag and 'href' in link_tag.attrs:
                link = urljoin('https://www.cfm.va.gov', link_tag["href"])
            else:
                link = ""

            if link:
                docx_response = requests.get(link)

                # Use headers to verify content type
                content_type = docx_response.headers.get('Content-Type')
                if content_type != 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    print(f"Unexpected content type for {link}: {content_type}")
                    continue

                if docx_response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
                        temp_docx.write(docx_response.content)
                        temp_docx_path = temp_docx.name

                    try:
                        doc = Document(temp_docx_path)
                        doc_text = '\n'.join([p.text for p in doc.paragraphs if p.text])

                        spec = {
                            "number": cols[0].text.strip(),
                            "title": cols[1].text.strip() if len(cols) > 1 else '',
                            "body": doc_text,
                            "link": link,
                        }
                        specs.append(spec)
                        print(f"Successfully scraped {cols[0].text.strip()} - {cols[1].text.strip() if len(cols) > 1 else ''}")

                    except Exception as e:
                        print(f"Failed to process Word document {link}: {e}")
                    finally:
                        os.remove(temp_docx_path)
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
# Save it
details_df.to_pickle("details_df.pkl")

# Check the specs DataFrame as well
print("Specifications DataFrame:")
print(specs_df.head())
print(specs_df.columns)
# Save it
specs_df.to_pickle("specs_df.pkl")