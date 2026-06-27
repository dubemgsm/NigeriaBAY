import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def process_datasets():
    raw_dir = "/workspaces/NigeriaBAY/data/raw"
    clean_dir = "/workspaces/NigeriaBAY/data/clean"
    processed_dir = "/workspaces/NigeriaBAY/data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    
    # --------------------------------------------------------------------------
    # 1. Process conflict.csv
    # --------------------------------------------------------------------------
    conflict_clean = os.path.join(clean_dir, "conflict.csv")
    conflict_processed = os.path.join(processed_dir, "conflict.csv")
    
    if os.path.exists(conflict_clean):
        print("\nProcessing conflict.csv...")
        df_conflict = pd.read_csv(conflict_clean)
        
        # Rename date_start to event_dates
        if "date_start" in df_conflict.columns:
            df_conflict["event_dates"] = df_conflict["date_start"]
            
        # Keep only required columns
        df_conf_out = df_conflict[["latitude", "longitude", "event_dates"]].copy()
        
        # Remove missing coordinates
        df_conf_out = df_conf_out.dropna(subset=["latitude", "longitude", "event_dates"])
        
        # Remove duplicates
        df_conf_out = df_conf_out.drop_duplicates()
        
        df_conf_out.to_csv(conflict_processed, index=False)
        print(f"Saved processed conflict data to {conflict_processed} (Shape: {df_conf_out.shape})")
    else:
        print(f"Clean conflict file not found at {conflict_clean}")

    # --------------------------------------------------------------------------
    # 2. Process schools.csv
    # --------------------------------------------------------------------------
    schools_raw = os.path.join(raw_dir, "nga_bay_schools_with_status_spatial.csv")
    schools_processed = os.path.join(processed_dir, "schools.csv")
    
    if os.path.exists(schools_raw):
        print("\nProcessing schools.csv...")
        df_schools = pd.read_csv(schools_raw)
        
        # Keep lgs_names (mapped from lga_name), status, coordinates (latitude, longitude)
        df_sch_out = df_schools[["lga_name", "status", "latitude", "longitude"]].copy()
        df_sch_out = df_sch_out.rename(columns={"lga_name": "lgs_names"})
        
        # Replace Tarmua with Tarmuwa to match expected spelling
        df_sch_out["lgs_names"] = df_sch_out["lgs_names"].replace({"Tarmua": "Tarmuwa"})
        
        # Drop missing values
        df_sch_out = df_sch_out.dropna()
        
        # Drop duplicates
        df_sch_out = df_sch_out.drop_duplicates()
        
        df_sch_out.to_csv(schools_processed, index=False)
        print(f"Saved processed schools data to {schools_processed} (Shape: {df_sch_out.shape})")
    else:
        print(f"Raw schools file not found at {schools_raw}")

    # --------------------------------------------------------------------------
    # 3. Process IDP.csv
    # --------------------------------------------------------------------------
    idp_clean = os.path.join(clean_dir, "IDP.csv")
    idp_processed = os.path.join(processed_dir, "IDP.csv")
    
    if os.path.exists(idp_clean):
        print("\nProcessing IDP.csv...")
        df_idp = pd.read_csv(idp_clean)
        
        # Filter for actual IDPs (exclude Returnees and Integrated)
        df_idp = df_idp[df_idp["Population Category"].astype(str).str.strip().str.startswith("IDP")].copy()
        
        # Keep coordinates (Latitude, Longitude) and IDP population (Individuals)
        df_idp_out = df_idp[["Latitude", "Longitude", "Individuals"]].copy()
        df_idp_out = df_idp_out.rename(columns={
            "Latitude": "latitude",
            "Longitude": "longitude",
            "Individuals": "idp_population"
        })
        
        # Drop missing values
        df_idp_out = df_idp_out.dropna(subset=["latitude", "longitude", "idp_population"])
        
        # Remove the IDP sites outside the BAY states (latitude 7.3534, longitude 10.1732)
        df_idp_out = df_idp_out[~((df_idp_out["latitude"] == 7.3534) & (df_idp_out["longitude"] == 10.1732))]
        
        # Drop duplicates
        df_idp_out = df_idp_out.drop_duplicates()
        
        df_idp_out.to_csv(idp_processed, index=False)
        print(f"Saved processed IDP data to {idp_processed} (Shape: {df_idp_out.shape})")
    else:
        print(f"Clean IDP file not found at {idp_clean}")

    # --------------------------------------------------------------------------
    # 4. Process population.csv (Aggregate population data at LGA level using spatial join)
    # --------------------------------------------------------------------------
    lga_shp_path = os.path.join(clean_dir, "nga_shp/nga_admin2.shp")
    population_processed = os.path.join(processed_dir, "population.csv")
    
    if os.path.exists(idp_clean) and os.path.exists(lga_shp_path):
        print("\nProcessing population.csv via spatial join...")
        df_idp = pd.read_csv(idp_clean)
        
        # Drop rows with missing coordinates
        df_idp_clean = df_idp.dropna(subset=["Latitude", "Longitude"]).copy()
        
        # Convert to GeoDataFrame
        geometry = [Point(xy) for xy in zip(df_idp_clean["Longitude"], df_idp_clean["Latitude"])]
        gdf_points = gpd.GeoDataFrame(df_idp_clean, geometry=geometry, crs="EPSG:4326")
        
        # Load LGA boundaries
        gdf_lgas = gpd.read_file(lga_shp_path)
        
        # Align CRS
        if gdf_points.crs != gdf_lgas.crs:
            gdf_points = gdf_points.to_crs(gdf_lgas.crs)
            
        # Spatial join to match points to LGA boundaries
        # We need LGA name column (adm2_name)
        joined_gdf = gpd.sjoin(gdf_points, gdf_lgas[["adm2_name", "geometry"]], how="inner", predicate="intersects")
        
        # Aggregate Individuals population by LGA name
        df_pop_agg = joined_gdf.groupby("adm2_name")["Individuals"].sum().reset_index()
        df_pop_agg = df_pop_agg.rename(columns={
            "adm2_name": "lgs_names",
            "Individuals": "population"
        })
        
        # Replace Tarmua with Tarmuwa to match expected spelling
        df_pop_agg["lgs_names"] = df_pop_agg["lgs_names"].replace({"Tarmua": "Tarmuwa"})
        
        # Drop missing values
        df_pop_agg = df_pop_agg.dropna()
        
        # Drop duplicates
        df_pop_agg = df_pop_agg.drop_duplicates()
        
        # Verify names like Tarmuwa, Girei
        lga_list = df_pop_agg["lgs_names"].tolist()
        print("Verifying sample LGA names in population dataset:")
        for name in ["Tarmuwa", "Girei"]:
            if name in lga_list:
                print(f"  - Verified: '{name}' exists in the dataset.")
            else:
                print(f"  - Warning: '{name}' NOT found in the dataset.")
                
        # Save to processed/population.csv
        df_pop_agg.to_csv(population_processed, index=False)
        print(f"Saved processed population data to {population_processed} (Shape: {df_pop_agg.shape})")
    else:
        print(f"Missing files for population spatial join: IDP.csv or nga_admin2.shp")

if __name__ == "__main__":
    process_datasets()
