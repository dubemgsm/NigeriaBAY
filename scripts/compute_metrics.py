import os
import pandas as pd

def compute_metrics():
    processed_dir = "/workspaces/NigeriaBAY/data/processed"
    summary_csv = os.path.join(processed_dir, "nga_bay_lga_summary.csv")
    
    if not os.path.exists(summary_csv):
        print(f"Summary file not found at {summary_csv}")
        return
        
    print("Loading LGA summary dataset...")
    df = pd.read_csv(summary_csv)
    
    # 1. Compute school_closure_rate = closed_schools / (total_schools + 1)
    df["school_closure_rate"] = df["closed_schools"] / (df["total_schools"] + 1)
    
    # 2. Helper function for Min-Max Normalization (0 to 1)
    def normalize_col(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return series * 0.0
        return (series - min_val) / (max_val - min_val)
        
    # Compute normalized conflict_intensity
    df["conflict_intensity"] = normalize_col(df["conflict_count"])
    
    # Compute normalized idp_density
    df["idp_density"] = normalize_col(df["idp_population"])
    
    # Compute normalized school_age_density
    df["school_age_density"] = normalize_col(df["school_age_population"])
    
    # Save the updated summary file
    df.to_csv(summary_csv, index=False)
    print(f"Computed metrics and saved back to {summary_csv}")
    print(f"New columns added: ['school_closure_rate', 'conflict_intensity', 'idp_density', 'school_age_density']")
    
    # Display the first 10 rows to verify values
    print("\nFirst 10 rows with computed metrics:")
    display_cols = [
        "LGA", "state", "school_closure_rate", "conflict_intensity", 
        "idp_density", "school_age_density"
    ]
    print(df[display_cols].head(10).to_string(index=False))

if __name__ == "__main__":
    compute_metrics()
