import os
import pandas as pd

def export_top_10():
    dataset_path = "/workspaces/NigeriaBAY/outputs/maps/final_dataset.csv"
    output_path = "/workspaces/NigeriaBAY/outputs/maps/top_10_lgas.csv"
    html_output_path = "/workspaces/NigeriaBAY/outputs/maps/top_10_lgas.html"
    
    if not os.path.exists(dataset_path):
        print(f"Error: final dataset not found at {dataset_path}")
        return
        
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    
    # Sort by risk_score descending
    df_sorted = df.sort_values(by="risk_score", ascending=False)
    
    # Select top 10
    top_10 = df_sorted.head(10).copy()
    top_10.insert(0, "rank", range(1, 11))
    
    # Save to top_10_lgas.csv
    top_10.to_csv(output_path, index=False)
    print(f"Successfully saved top 10 LGAs to {output_path}")
    
    # Create HTML table format for display in dashboard
    # Select presentation columns
    cols_presentation = [
        "rank", "LGA", "state", "risk_score", "school_age_population", 
        "idp_population", "conflict_count", "closed_schools"
    ]
    df_html = top_10[cols_presentation].copy()
    df_html["rank"] = df_html["rank"].map(lambda x: f"#{x}")
    df_html.columns = [
        "Rank", "LGA Name", "State", "Risk Score", "School-Age Pop", 
        "IDP Population", "Conflict Count", "Closed Schools"
    ]
    
    # Round risk score for display
    df_html["Risk Score"] = df_html["Risk Score"].round(4)
    
    # Generate HTML Table
    html_table = df_html.to_html(index=False, classes="top-lgas-table")
    
    # Wrap in container
    html_content = f"<div class=\"table-container\">\n{html_table}\n</div>"
    
    # Save HTML table
    with open(html_output_path, "w") as f:
        f.write(html_content)
    print(f"Successfully saved HTML table format to {html_output_path}")
    
    # Print the top 10
    print("\n--- TOP 10 LGAS BY RISK SCORE ---")
    print(top_10.to_string(index=False))

if __name__ == "__main__":
    export_top_10()
