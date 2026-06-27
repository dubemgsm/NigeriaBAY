import os
import pandas as pd

def clean_data():
    raw_dir = "/workspaces/NigeriaBAY/data/raw"
    clean_dir = "/workspaces/NigeriaBAY/data/clean"
    os.makedirs(clean_dir, exist_ok=True)
    
    dtm_path = os.path.join(raw_dir, "DTM Nigeria Site Assessment Round 50.xlsx")
    conflict_path = os.path.join(raw_dir, "conflict_data_nga.csv")
    
    idp_out = os.path.join(clean_dir, "IDP.csv")
    conflict_out = os.path.join(clean_dir, "conflict.csv")
    
    bay_states = ["Adamawa", "Borno", "Yobe"]
    
    # 1. Clean DTM Site Assessment
    if os.path.exists(dtm_path):
        print(f"Loading DTM data sheet...")
        df_dtm = pd.read_excel(dtm_path, sheet_name="Data")
        print(f"Original DTM shape: {df_dtm.shape}")
        
        # Filter for BAY states
        df_dtm_filtered = df_dtm[df_dtm["State"].astype(str).str.strip().str.title().isin(bay_states)].copy()
        
        # Save to clean/IDP.csv
        df_dtm_filtered.to_csv(idp_out, index=False)
        print(f"Saved filtered DTM data to {idp_out} (Shape: {df_dtm_filtered.shape})")
        print("DTM state counts:")
        print(df_dtm_filtered["State"].value_counts())
    else:
        print(f"Error: DTM file not found at {dtm_path}")
        
    # 2. Clean Conflict Data
    if os.path.exists(conflict_path):
        print(f"\nLoading Conflict CSV data...")
        df_conflict = pd.read_csv(conflict_path)
        print(f"Original Conflict shape: {df_conflict.shape}")
        
        # Filter for BAY states in adm_1
        bay_conflict_states = ["adamawa state", "borno state", "yobe state"]
        df_conflict_filtered = df_conflict[
            df_conflict["adm_1"].astype(str).str.strip().str.lower().isin(bay_conflict_states)
        ].copy()
        
        # Save to clean/conflict.csv
        df_conflict_filtered.to_csv(conflict_out, index=False)
        print(f"Saved filtered Conflict data to {conflict_out} (Shape: {df_conflict_filtered.shape})")
        print("Conflict state counts:")
        print(df_conflict_filtered["adm_1"].value_counts())
    else:
        print(f"Error: Conflict file not found at {conflict_path}")

if __name__ == "__main__":
    clean_data()
