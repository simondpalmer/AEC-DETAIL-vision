from pdf2image import convert_from_path
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()
hf_token = os.getenv('HUGGINGFACE_TOKEN')

# Web Scraping

images = convert_from_path('https://www.cfm.va.gov/til/sDetail/Div00SpclSect/SD000115-26.pdf')

for i in range(len(images)):
  
      # Save pages as images in the pdf
    images[i].save('page'+ str(i) +'.jpg', 'JPEG')