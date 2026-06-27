import os
import pandas as pd
import geopandas as gpd

def convert_to_spatial():
    processed_dir = "/workspaces/NigeriaBAY/data/processed"
    
    datasets = {
        "conflict": {
            "csv": os.path.join(processed_dir, "conflict.csv"),
            "lat": "latitude",
            "lon": "longitude"
        },
        "schools": {
            "csv": os.path.join(processed_dir, "schools.csv"),
            "lat": "latitude",
            "lon": "longitude"
        },
        "IDP": {
            "csv": os.path.join(processed_dir, "IDP.csv"),
            "lat": "latitude",
            "lon": "longitude"
        }
    }
    
    for name, info in datasets.items():
        csv_path = info["csv"]
        if not os.path.exists(csv_path):
            print(f"File not found: {csv_path}")
            continue
            
        print(f"\nConverting {name} dataset to GeoDataFrame...")
        df = pd.read_csv(csv_path)
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(
            df, 
            geometry=gpd.points_from_xy(df[info["lon"]], df[info["lat"]]),
            crs="EPSG:4326"
        )
        
        print(f"Created GeoDataFrame shape: {gdf.shape}")
        print(f"CRS set to: {gdf.crs}")
        
        # Save as GeoJSON
        geojson_path = os.path.join(processed_dir, f"{name}.geojson")
        gdf.to_file(geojson_path, driver="GeoJSON")
        print(f"Saved GeoJSON to {geojson_path}")
        
        # Save as Shapefile (requires creating shapefile components)
        shp_path = os.path.join(processed_dir, f"{name}.shp")
        # Shapefile column names must be <= 10 characters, geopandas handles this but we'll print confirmation
        gdf.to_file(shp_path)
        print(f"Saved Shapefile to {shp_path}")

if __name__ == "__main__":
    convert_to_spatial()
