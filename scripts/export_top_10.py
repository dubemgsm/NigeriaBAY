import os
import pandas as pd

def export_top_10():
    dataset_path = "/workspaces/NigeriaBAY/outputs/maps/final_dataset.csv"
    output_path = "/workspaces/NigeriaBAY/outputs/maps/top_10_lgas.csv"
    
    if not os.path.exists(dataset_path):
        print(f"Error: final dataset not found at {dataset_path}")
        return
        
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    
    # Sort by risk_score descending
    df_sorted = df.sort_values(by="risk_score", ascending=False)
    
    # Select top 10
    top_10 = df_sorted.head(10)
    
    # Save to top_10_lgas.csv
    top_10.to_csv(output_path, index=False)
    print(f"Successfully saved top 10 LGAs to {output_path}")
    
    # Print the top 10
    print("\n--- TOP 10 LGAS BY RISK SCORE ---")
    print(top_10.to_string(index=False))

if __name__ == "__main__":
    export_top_10()
