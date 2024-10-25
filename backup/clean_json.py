import pandas as pd
import json

# Consider double-checking the JSON line structure
with open('./data/metadata.jsonl', 'r') as f:
    data = [json.loads(line) for line in f]

# Sample transformation if you have nested JSON
for entry in data:
    if isinstance(entry['detail_description'], list):
        for dialogue in entry['detail_description']:
            dialogue['from'] = str(dialogue['from'])
            dialogue['value'] = str(dialogue['value'])

# Convert back to DataFrame to inspect
df = pd.DataFrame(data)

# Ensure no complex nested structures are present
# Flatten anything necessary into strings or simpler representations if needed
df['detail_description'] = df['detail_description'].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)

# Optionally save to a new .jsonl for clarity
df.to_json('metadata_cleaned.jsonl', orient='records', lines=True)