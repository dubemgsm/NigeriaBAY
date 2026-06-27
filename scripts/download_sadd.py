import os
import requests
import pandas as pd

def download_and_inspect_sadd():
    raw_dir = "/workspaces/NigeriaBAY/data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    
    url = "https://data.humdata.org/dataset/d38cdaa8-3a19-4a7b-a166-5a44c61e8182/resource/da740532-c591-44b9-b08d-f17cd9b1276e/download/2025_humanitarian_profile_saad_02072024.xlsx"
    target_xlsx = os.path.join(raw_dir, "2025_humanitarian_profile_saad_02072024.xlsx")
    
    print(f"Downloading SADD Humanitarian Profile from {url}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(target_xlsx, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Saved raw Excel to {target_xlsx}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        return

    # Load Excel to check sheets
    print("Reading Excel sheets...")
    xls = pd.ExcelFile(target_xlsx)
    print(f"Sheets in Excel: {xls.sheet_names}")
    
    for sheet in xls.sheet_names[:3]:
        df = pd.read_excel(target_xlsx, sheet_name=sheet)
        print(f"\nSheet name: {sheet}")
        print(f"Shape: {df.shape}")
        print("Columns:")
        print(df.columns.tolist()[:15])
        print("First few rows:")
        print(df.head(2))

if __name__ == "__main__":
    download_and_inspect_sadd()
