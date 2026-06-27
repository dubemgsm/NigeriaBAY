import os
import geopandas as gpd
import pandas as pd

def merge_lga_data():
    processed_dir = "/workspaces/NigeriaBAY/data/processed"
    raw_dir = "/workspaces/NigeriaBAY/data/raw"
    clean_dir = "/workspaces/NigeriaBAY/data/clean"
    
    # 1. Load LGA Boundaries as the baseline
    lga_shp = os.path.join(clean_dir, "nga_shp/nga_admin2.shp")
    if not os.path.exists(lga_shp):
        print(f"LGA boundary shapefile not found at {lga_shp}")
        return
        
    print("Loading LGA boundaries...")
    gdf_lgas = gpd.read_file(lga_shp)
    
    # Keep only adm2_name (LGA) and adm1_name (state)
    df_base = gdf_lgas[["adm2_name", "adm1_name", "geometry"]].copy()
    df_base = df_base.rename(columns={
        "adm2_name": "LGA",
        "adm1_name": "state"
    })
    
    # Ensure standard names spelling
    df_base["LGA"] = df_base["LGA"].replace({"Tarmua": "Tarmuwa"})
    
    print(f"Baseline LGA count: {len(df_base)}")

    # --------------------------------------------------------------------------
    # 2. Count Conflict Events per LGA
    # --------------------------------------------------------------------------
    conflict_path = os.path.join(processed_dir, "conflict.geojson")
    if os.path.exists(conflict_path):
        print("Loading and joining conflict points...")
        gdf_conflict = gpd.read_file(conflict_path)
        
        # Spatial join
        joined = gpd.sjoin(gdf_conflict, df_base[["LGA", "geometry"]], how="inner", predicate="intersects")
        conflict_counts = joined.groupby("LGA").size().reset_index(name="conflict_count")
        
        # Merge into baseline
        df_base = pd.merge(df_base, conflict_counts, on="LGA", how="left")
    else:
        print("Conflict spatial file not found.")
        df_base["conflict_count"] = 0
        
    df_base["conflict_count"] = df_base["conflict_count"].fillna(0).astype(int)

    # --------------------------------------------------------------------------
    # 3. Count Schools per LGA
    # --------------------------------------------------------------------------
    schools_path = os.path.join(processed_dir, "schools.geojson")
    if os.path.exists(schools_path):
        print("Loading and joining school points...")
        gdf_schools = gpd.read_file(schools_path)
        
        # Spatial join
        joined = gpd.sjoin(gdf_schools, df_base[["LGA", "geometry"]], how="inner", predicate="intersects")
        
        # Calculate counts
        schools_stats = joined.groupby("LGA").agg(
            total_schools=("status", "count"),
            open_schools=("status", lambda x: (x == "Open").sum()),
            closed_schools=("status", lambda x: x.isin(["Closed", "Close"]).sum())
        ).reset_index()
        
        # Merge into baseline
        df_base = pd.merge(df_base, schools_stats, on="LGA", how="left")
    else:
        print("Schools spatial file not found.")
        df_base["total_schools"] = 0
        df_base["open_schools"] = 0
        df_base["closed_schools"] = 0
        
    for col in ["total_schools", "open_schools", "closed_schools"]:
        df_base[col] = df_base[col].fillna(0).astype(int)

    # --------------------------------------------------------------------------
    # 4. Sum IDP Population per LGA
    # --------------------------------------------------------------------------
    idp_path = os.path.join(processed_dir, "IDP.geojson")
    if os.path.exists(idp_path):
        print("Loading and joining IDP points...")
        gdf_idp = gpd.read_file(idp_path)
        
        # Spatial join
        joined = gpd.sjoin(gdf_idp, df_base[["LGA", "geometry"]], how="inner", predicate="intersects")
        
        # Aggregate population
        idp_sum = joined.groupby("LGA")["idp_population"].sum().reset_index()
        
        # Merge into baseline
        df_base = pd.merge(df_base, idp_sum, on="LGA", how="left")
    else:
        print("IDP spatial file not found.")
        df_base["idp_population"] = 0
        
    df_base["idp_population"] = df_base["idp_population"].fillna(0).astype(int)

    # --------------------------------------------------------------------------
    # 5. Merge School-Age Population per LGA (tabular join)
    # --------------------------------------------------------------------------
    school_age_path = os.path.join(processed_dir, "school_age_population.csv")
    if os.path.exists(school_age_path):
        print("Loading and merging school age population...")
        df_school_age = pd.read_csv(school_age_path)
        
        # Clean LGA name and align Tarmua with Tarmuwa
        df_school_age["lga_clean"] = df_school_age["lga"].astype(str).str.strip().str.replace("Tarmua", "Tarmuwa")
        
        # Drop columns except lga_clean and school_age_total
        df_school_age_sub = df_school_age[["lga_clean", "school_age_total"]].copy()
        df_school_age_sub = df_school_age_sub.rename(columns={
            "lga_clean": "LGA",
            "school_age_total": "school_age_population"
        })
        
        # Merge into baseline
        df_base = pd.merge(df_base, df_school_age_sub, on="LGA", how="left")
    else:
        print("School-age population CSV not found.")
        df_base["school_age_population"] = 0
        
    df_base["school_age_population"] = df_base["school_age_population"].fillna(0).astype(int)

    # --------------------------------------------------------------------------
    # 6. Save the final merged dataframe
    # --------------------------------------------------------------------------
    # Drop geometry column for tabular CSV output
    df_final = pd.DataFrame(df_base.drop(columns=["geometry"]))
    
    # Re-order columns as requested
    cols = [
        "LGA", "state", "conflict_count", "total_schools", 
        "open_schools", "closed_schools", "idp_population", "school_age_population"
    ]
    df_final = df_final[cols]
    
    out_csv = os.path.join(processed_dir, "nga_bay_lga_summary.csv")
    df_final.to_csv(out_csv, index=False)
    print(f"\nSaved final merged LGA summary dataset to {out_csv} (Shape: {df_final.shape})")
    
    # Display the first 10 rows
    print("\nFirst 10 rows of final merged dataframe:")
    print(df_final.head(10).to_string(index=False))

if __name__ == "__main__":
    merge_lga_data()
