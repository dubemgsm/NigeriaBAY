import os
import geopandas as gpd
import pandas as pd
import re

def normalize_name(name):
    if not isinstance(name, str):
        return ""
    name = name.lower()
    name = re.sub(r'[^a-z0-9\s]', ' ', name)
    name = ' '.join(name.split())
    common_words = [
        "primary", "secondary", "school", "schools", "islamiyya", "nomadic", 
        "junior", "senior", "comprehensive", "government", "ltd", "gss", "gps", 
        "jss", "pri", "sec", "sch", "academic", "academy"
    ]
    words = name.split()
    filtered_words = [w for w in words if w not in common_words]
    return ' '.join(filtered_words) if filtered_words else name

def normalize_lga(name):
    if not isinstance(name, str):
        return ""
    name = name.lower()
    # Remove characters like hyphens or slashes to make matching robust
    name = re.sub(r'[^a-z0-9]', '', name)
    return name

def merge_schools_spatial():
    raw_dir = "/workspaces/NigeriaBAY/data/raw"
    immap_csv = os.path.join(raw_dir, "nga_schools_june_2019/nga_north_east_education_sector_school_list_19062019.csv")
    schools_shp = os.path.join(raw_dir, "NGA_Education/NGA_Education.shp")
    lga_shp = os.path.join(raw_dir, "nga_shp/nga_admin2.shp")
    
    if not all(os.path.exists(f) for f in [immap_csv, schools_shp, lga_shp]):
        print("Missing required files for spatial join.")
        return
        
    print("Loading datasets...")
    df_immap = pd.read_csv(immap_csv, encoding='latin1')
    gdf_schools = gpd.read_file(schools_shp)
    gdf_lgas = gpd.read_file(lga_shp)
    
    print(f"Schools count in GRID3: {len(gdf_schools)}")
    print(f"LGA polygons count: {len(gdf_lgas)}")
    
    # Filter schools for BAY states (AD, BR, YO)
    bay_codes = ["AD", "BR", "YO"]
    gdf_schools = gdf_schools[gdf_schools["state_code"].isin(bay_codes)].copy()
    print(f"Filtered schools in BAY states: {len(gdf_schools)}")
    
    # Ensure matching CRS for spatial join
    print("Aligning CRS...")
    if gdf_schools.crs != gdf_lgas.crs:
        print(f"Re-projecting schools from {gdf_schools.crs} to {gdf_lgas.crs}...")
        gdf_schools = gdf_schools.to_crs(gdf_lgas.crs)
        
    # Perform spatial join to attach LGA name to school points
    print("Performing spatial join...")
    # gdf_lgas has LGA names (usually columns like 'adm2_name' or 'adm2_en')
    print("LGA columns:", gdf_lgas.columns.tolist())
    
    # Look for LGA name column in shapefile
    lga_name_col = None
    for col in gdf_lgas.columns:
        if col.lower() in ["adm2_name", "adm2_en", "lga_name", "local"]:
            lga_name_col = col
            break
    if not lga_name_col:
        lga_name_col = gdf_lgas.columns[0]
        
    print(f"Using LGA name column from shapefile: {lga_name_col}")
    
    # Do spatial join
    schools_joined = gpd.sjoin(gdf_schools, gdf_lgas[[lga_name_col, "geometry"]], how="left", predicate="intersects")
    print(f"Schools after spatial join: {len(schools_joined)}")
    
    # Extract coordinates
    schools_joined = schools_joined.to_crs("EPSG:4326")
    schools_joined["longitude"] = schools_joined.geometry.x
    schools_joined["latitude"] = schools_joined.geometry.y
    
    # Prepare for matching
    df_immap["state_clean"] = df_immap["State Name"].astype(str).str.strip().str.title()
    state_mapping = {"AD": "Adamawa", "BR": "Borno", "YO": "Yobe"}
    schools_joined["state_clean"] = schools_joined["state_code"].map(state_mapping)
    
    # Normalize LGA names in both datasets
    df_immap["lga_norm"] = df_immap["LGA Name"].apply(normalize_lga)
    schools_joined["lga_norm"] = schools_joined[lga_name_col].apply(normalize_lga)
    
    # Normalize school names
    df_immap["norm_name"] = df_immap["School Name"].apply(normalize_name)
    schools_joined["norm_name"] = schools_joined["name"].apply(normalize_name)
    
    # Drop rows with empty names
    df_immap = df_immap[df_immap["norm_name"] != ""]
    schools_joined = schools_joined[schools_joined["norm_name"] != ""]
    
    # Perform inner merge on state, LGA, and normalized school name
    print("Merging on state, LGA, and normalized school name...")
    merged_df = pd.merge(
        schools_joined,
        df_immap[["state_clean", "lga_norm", "norm_name", "School Status", "School Level", "School Type", "School Name"]],
        on=["state_clean", "lga_norm", "norm_name"],
        how="inner"
    )
    
    print(f"Merged schools count (with duplicates): {len(merged_df)}")
    merged_df = merged_df.drop_duplicates(subset=["id"])
    print(f"Unique matched schools count: {len(merged_df)}")
    
    # Let's save this as the final clean dataset!
    # Rename columns for clarity
    merged_df = merged_df.rename(columns={
        "name": "school_name_grid3",
        "School Name": "school_name_immap",
        lga_name_col: "lga_name",
        "School Status": "status",
        "School Level": "education_level",
        "School Type": "school_type"
    })
    
    cols_to_save = [
        "id", "state_clean", "lga_name", "school_name_grid3", "school_name_immap",
        "status", "education_level", "school_type", "latitude", "longitude",
        "category", "subtype", "management"
    ]
    
    # Filter columns that exist
    cols_to_save = [c for c in cols_to_save if c in merged_df.columns]
    
    out_df = pd.DataFrame(merged_df[cols_to_save])
    # Rename state_clean to state
    out_df = out_df.rename(columns={"state_clean": "state"})
    
    out_csv = os.path.join(raw_dir, "nga_bay_schools_with_status_spatial.csv")
    out_df.to_csv(out_csv, index=False)
    print(f"Saved spatially matched schools with status and coordinates to {out_csv}")
    
    print("\nMatched Status distribution:")
    print(out_df["status"].value_counts(dropna=False))
    
if __name__ == "__main__":
    merge_schools_spatial()
