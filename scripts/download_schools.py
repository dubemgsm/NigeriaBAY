import os
import zipfile
import requests
import geopandas as gpd
import pandas as pd
import glob

def download_and_process_shp():
    raw_dir = "/workspaces/NigeriaBAY/data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    
    url = "https://data.humdata.org/dataset/ec228c18-8edc-4f3c-94c9-a6b946af7229/resource/1a064a21-ffcf-4fb8-a0a6-5cf811d94664/download/nga_education.zip"
    target_zip = os.path.join(raw_dir, "NGA_Education.zip")
    extract_dir = os.path.join(raw_dir, "NGA_Education")
    
    print(f"Downloading ZIP dataset from {url}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(target_zip, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Saved raw ZIP to {target_zip}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        return

    print("Extracting ZIP file...")
    with zipfile.ZipFile(target_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Extracted to {extract_dir}")
    
    # List files
    shp_files = glob.glob(os.path.join(extract_dir, "**/*.shp"), recursive=True)
    print(f"Found Shapefiles: {shp_files}")
    
    if not shp_files:
        print("No shapefile found!")
        return
        
    shp_path = shp_files[0]
    print(f"Reading shapefile: {shp_path}...")
    gdf = gpd.read_file(shp_path)
    print("Columns in shapefile:")
    print(gdf.columns.tolist())
    print(f"Shape: {gdf.shape}")
    print("First 3 rows:")
    print(gdf.head(3))
    
    # Filter for BAY states: state_code AD, BR, YO
    print("Filtering for BAY states (AD, BR, YO)...")
    bay_codes = ["AD", "BR", "YO"]
    filtered_gdf = gdf[gdf["state_code"].isin(bay_codes)].copy()
    print(f"Filtered shape: {filtered_gdf.shape}")
    
    if filtered_gdf.empty:
        print("No records found for BAY states!")
        return
        
    # Extract coordinates from geometry
    # Check coordinate reference system (CRS) - convert to EPSG:4326 if not already, to get latitude/longitude
    print(f"Current CRS: {filtered_gdf.crs}")
    if filtered_gdf.crs != "EPSG:4326":
        print("Re-projecting to EPSG:4326 (WGS 84)...")
        filtered_gdf = filtered_gdf.to_crs("EPSG:4326")
        
    # Extract longitude and latitude
    filtered_gdf["longitude"] = filtered_gdf.geometry.x
    filtered_gdf["latitude"] = filtered_gdf.geometry.y
    
    # Check if there is a status column
    status_col = None
    for col in filtered_gdf.columns:
        if "status" in col.lower() or "operational" in col.lower():
            status_col = col
            break
            
    # Save the output CSV with names, status, and coordinates
    # Let's map state codes to full state names for clarity
    state_mapping = {"AD": "Adamawa", "BR": "Borno", "YO": "Yobe"}
    filtered_gdf["state_name"] = filtered_gdf["state_code"].map(state_mapping)
    
    # Select columns of interest
    cols_to_save = ["state_name", "name", "category", "subtype", "management", "education", "latitude", "longitude"]
    if status_col:
        cols_to_save.append(status_col)
        
    # We will also keep other columns if they are useful
    out_df = pd.DataFrame(filtered_gdf)
    out_csv = os.path.join(raw_dir, "nga_bay_schools.csv")
    out_df.to_csv(out_csv, index=False)
    
    print(f"Saved BAY states schools with coordinates to {out_csv}")
    print(f"Columns saved: {out_df.columns.tolist()}")
    print(f"Total schools saved: {len(out_df)}")
    
    # Print status values
    if status_col:
        print("\nStatus distribution:")
        print(out_df[status_col].value_counts(dropna=False))
    else:
        print("\nNo status column found in shapefile columns!")
        
if __name__ == "__main__":
    download_and_process_shp()
