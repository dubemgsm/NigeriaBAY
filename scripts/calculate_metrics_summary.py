import os
import pandas as pd

def calculate_summary():
    summary_path = "/workspaces/NigeriaBAY/data/processed/nga_bay_lga_summary.csv"
    
    if not os.path.exists(summary_path):
        print(f"Error: summary dataset not found at {summary_path}")
        return
        
    df = pd.read_csv(summary_path)
    
    # 1. total_idps = sum of idp_population
    total_idps = int(df["idp_population"].sum())
    
    # 2. total_schools = sum of total_schools
    total_schools = int(df["total_schools"].sum())
    
    # 3. total_closed_schools = sum of closed_schools
    total_closed_schools = int(df["closed_schools"].sum())
    
    # 4. closed_school_percentage = (total_closed_schools / total_schools) * 100
    if total_schools > 0:
        closed_school_percentage = (total_closed_schools / total_schools) * 100
    else:
        closed_school_percentage = 0.0
        
    # 5. highest_risk_lga = LGA with highest risk_score
    idx_max = df["risk_score"].idxmax()
    highest_risk_row = df.loc[idx_max]
    highest_risk_lga = highest_risk_row["LGA"]
    highest_risk_score = highest_risk_row["risk_score"]
    highest_risk_state = highest_risk_row["state"]
    
    # Print results clearly
    print("==================================================")
    print("        BAY STATES SUMMARY STATISTICAL METRICS     ")
    print("==================================================")
    print(f"total_idps = {total_idps}")
    print(f"total_schools = {total_schools}")
    print(f"total_closed_schools = {total_closed_schools}")
    print(f"closed_school_percentage = {closed_school_percentage:.2f}%")
    print(f"highest_risk_lga = {highest_risk_lga} ({highest_risk_state} State, risk_score: {highest_risk_score:.6f})")
    print("==================================================")

if __name__ == "__main__":
    calculate_summary()
