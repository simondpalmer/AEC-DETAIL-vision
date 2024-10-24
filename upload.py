from datasets import load_dataset
from dotenv import load_dotenv
import os

load_dotenv()
hf_token = os.getenv('HUGGINGFACE_TOKEN')
# Sign in with Hug face CLI

repo_id = "simondavidpalmer/AEC-VA-details-spec-dataset"

dataset = load_dataset("imagefolder", data_dir="/data", split="train")
dataset.push_to_hub(repo_id)

print(f"Dataset published at: https://huggingface.co/datasets/{repo_id}")