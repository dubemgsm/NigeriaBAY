import os
import pandas as pd

def compute_risk_score():
    processed_dir = "/workspaces/NigeriaBAY/data/processed"
    summary_csv = os.path.join(processed_dir, "nga_bay_lga_summary.csv")
    
    if not os.path.exists(summary_csv):
        print(f"Summary file not found at {summary_csv}")
        return
        
    print("Loading LGA summary dataset...")
    df = pd.read_csv(summary_csv)
    
    # 1. Compute raw risk score
    # Formula: (conflict_intensity * 0.30) + (idp_density * 0.25) + (school_closure_rate * 0.25) + (school_age_density * 0.20)
    df["risk_score"] = (
        (df["conflict_intensity"] * 0.30) + 
        (df["idp_density"] * 0.25) + 
        (df["school_closure_rate"] * 0.25) + 
        (df["school_age_density"] * 0.20)
    )
    
    # 2. Normalize final score between 0 and 1
    min_val = df["risk_score"].min()
    max_val = df["risk_score"].max()
    
    if max_val != min_val:
        df["risk_score"] = (df["risk_score"] - min_val) / (max_val - min_val)
    else:
        df["risk_score"] = 0.0
        
    # Save the updated summary file
    df.to_csv(summary_csv, index=False)
    print(f"Computed normalized risk_score and saved back to {summary_csv}")
    
    # Display the top 10 most vulnerable LGAs (sorted by risk_score descending)
    print("\nTop 10 Most Vulnerable LGAs (Sorted by Risk Score):")
    display_cols = [
        "LGA", "state", "conflict_intensity", "idp_density", 
        "school_closure_rate", "school_age_density", "risk_score"
    ]
    top_10 = df.sort_values(by="risk_score", ascending=False).head(10)
    print(top_10[display_cols].to_string(index=False))

if __name__ == "__main__":
    compute_risk_score()
