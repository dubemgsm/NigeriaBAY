import os
import pandas as pd

def export_dataset():
    summary_path = "/workspaces/NigeriaBAY/data/processed/nga_bay_lga_summary.csv"
    output_dir = "/workspaces/NigeriaBAY/outputs/maps"
    output_path = os.path.join(output_dir, "final_dataset.csv")
    
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(summary_path):
        print(f"Error: summary dataset not found at {summary_path}")
        return
        
    print(f"Loading summary dataset from {summary_path}...")
    df = pd.read_csv(summary_path)
    
    # Columns to include
    cols_to_include = [
        "LGA",
        "state",
        "risk_score",
        "school_age_population",
        "idp_population",
        "conflict_count",
        "closed_schools"
    ]
    
    # Export and save
    df_export = df[cols_to_include].copy()
    
    df_export.to_csv(output_path, index=False)
    print(f"Successfully exported final dataset to {output_path} (Shape: {df_export.shape})")
    
    # Print sample data
    print("\nFirst 5 rows of final exported dataset:")
    print(df_export.head(5).to_string(index=False))

if __name__ == "__main__":
    export_dataset()
