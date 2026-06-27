import os
import glob
import geopandas as gpd

def clean_shapefiles():
    raw_dir = "/workspaces/NigeriaBAY/data/raw/nga_shp"
    clean_dir = "/workspaces/NigeriaBAY/data/clean/nga_shp"
    os.makedirs(clean_dir, exist_ok=True)
    
    bay_states = ["Adamawa", "Borno", "Yobe"]
    
    # Load Admin 1 to create the BAY states union geometry for spatial operations
    admin1_path = os.path.join(raw_dir, "nga_admin1.shp")
    if not os.path.exists(admin1_path):
        print(f"Error: Admin 1 shapefile not found at {admin1_path}")
        return
        
    admin1_df = gpd.read_file(admin1_path)
    bay_admin1 = admin1_df[admin1_df["adm1_name"].isin(bay_states)]
    
    # Use union_all() if available, fallback to unary_union
    if hasattr(bay_admin1.geometry, "union_all"):
        bay_union = bay_admin1.geometry.union_all()
    else:
        bay_union = bay_admin1.geometry.unary_union
        
    shp_files = glob.glob(os.path.join(raw_dir, "*.shp"))
    
    for shp_path in sorted(shp_files):
        base = os.path.basename(shp_path)
        name, ext = os.path.splitext(base)
        print(f"\n--- Processing {base} ---")
        
        df = gpd.read_file(shp_path)
        print(f"Original shape: {df.shape}")
        
        filtered_df = None
        
        # Determine filtering strategy based on filename and columns
        if "admin1" in name:
            filtered_df = df[df["adm1_name"].isin(bay_states)]
        elif "admin2" in name:
            filtered_df = df[df["adm1_name"].isin(bay_states)]
        elif "admin3" in name:
            filtered_df = df[df["adm1_name"].isin(bay_states)]
        elif "admincapitals" in name:
            filtered_df = df[df["adm1_name"].isin(bay_states)]
        elif "adminpoints" in name:
            filtered_df = df[df["adm1_name"].isin(bay_states)]
        elif "senatorialdistricts" in name:
            if "adm1_en" in df.columns:
                filtered_df = df[df["adm1_en"].isin(bay_states)]
            elif "admin1name" in df.columns:
                filtered_df = df[df["admin1name"].isin(bay_states)]
        elif "adminlines" in name:
            # Clip spatially and keep only line geometry types to avoid mixed types
            clipped = gpd.clip(df, bay_union)
            filtered_df = clipped[clipped.geometry.type.isin(["LineString", "MultiLineString"])]
        elif "admin0" in name:
            # Clip spatially and keep only polygon geometry types
            clipped = gpd.clip(df, bay_union)
            filtered_df = clipped[clipped.geometry.type.isin(["Polygon", "MultiPolygon"])]
            # Update attributes to reflect the BAY region
            for col in ["adm0_name", "adm0_name1", "adm0_name2", "adm0_name3", "adm0_en", "admin0name"]:
                if col in filtered_df.columns:
                    filtered_df[col] = "BAY States"
        else:
            # Fallback based on columns
            state_cols = ["adm1_name", "adm1_en", "admin1name", "state"]
            found_col = None
            for col in state_cols:
                if col in df.columns:
                    found_col = col
                    break
            
            if found_col:
                filtered_df = df[df[found_col].isin(bay_states)]
            else:
                # If no state column found, clip spatially and keep geom type of original first element
                clipped = gpd.clip(df, bay_union)
                orig_geom_type = df.geometry.iloc[0].geom_type if not df.empty else ""
                if "Polygon" in orig_geom_type or "MultiPolygon" in orig_geom_type:
                    filtered_df = clipped[clipped.geometry.type.isin(["Polygon", "MultiPolygon"])]
                elif "LineString" in orig_geom_type or "MultiLineString" in orig_geom_type:
                    filtered_df = clipped[clipped.geometry.type.isin(["LineString", "MultiLineString"])]
                elif "Point" in orig_geom_type or "MultiPoint" in orig_geom_type:
                    filtered_df = clipped[clipped.geometry.type.isin(["Point", "MultiPoint"])]
                else:
                    filtered_df = clipped
                
        if filtered_df is not None and not filtered_df.empty:
            out_path = os.path.join(clean_dir, base)
            filtered_df.to_file(out_path)
            print(f"Saved to {out_path}")
            print(f"New shape: {filtered_df.shape}")
        else:
            print("Filtered result is empty. Skipping.")

if __name__ == "__main__":
    clean_shapefiles()
