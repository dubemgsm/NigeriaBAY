import os
import pandas as pd

def calculate_summary():
    summary_path = "/workspaces/NigeriaBAY/data/processed/nga_bay_lga_summary.csv"
    
    if not os.path.exists(summary_path):
        print(f"Error: summary dataset not found at {summary_path}")
        return
        
    df = pd.read_csv(summary_path)
    
    # 1. Total IDP population
    total_idps = int(df["idp_population"].sum())
    
    # 2. Total schools
    total_schools = int(df["total_schools"].sum())
    
    # 3. Closed school ratio = total closed / total schools
    total_closed = int(df["closed_schools"].sum())
    if total_schools > 0:
        closed_school_ratio = total_closed / total_schools
    else:
        closed_school_ratio = 0.0
        
    # 4. Highest risk LGA (max risk_score)
    idx_max = df["risk_score"].idxmax()
    highest_risk_row = df.loc[idx_max]
    highest_risk_lga = highest_risk_row["LGA"]
    highest_risk_score = highest_risk_row["risk_score"]
    highest_risk_state = highest_risk_row["state"]
    
    # Print results clearly
    print("==================================================")
    print("        BAY STATES SUMMARY STATISTICAL METRICS     ")
    print("==================================================")
    print(f"Total IDPs (aggregated):  {total_idps:,}")
    print(f"Total Schools (recorded):  {total_schools:,}")
    print(f"Total Closed Schools:      {total_closed:,}")
    print(f"Closed School Ratio:       {closed_school_ratio:.4f} ({closed_school_ratio * 100:.2f}%)")
    print(f"Highest Risk LGA:          {highest_risk_lga} ({highest_risk_state} State)")
    print(f"  - Risk Score:            {highest_risk_score:.6f}")
    print("==================================================")

if __name__ == "__main__":
    calculate_summary()
