import os
import pandas as pd

def process_sadd():
    target_xlsx = "/workspaces/NigeriaBAY/data/raw/2025_humanitarian_profile_saad_02072024.xlsx"
    processed_dir = "/workspaces/NigeriaBAY/data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    out_csv = os.path.join(processed_dir, "school_age_population.csv")
    
    if not os.path.exists(target_xlsx):
        print(f"File not found: {target_xlsx}")
        return
        
    print("Parsing SADD Humanitarian Profile...")
    # Read without header
    df = pd.read_excel(target_xlsx, header=None)
    
    # Extract headers from Row 0 (it contains the actual column names)
    raw_headers = df.iloc[0].tolist()
    
    # Clean the headers list (fill in nans with custom names or descriptions from the tags/context)
    clean_headers = [
        "state", "state_pcode", "lga", "pcode",
        "idps_girls", "idps_boys", "idps_women", "idps_men", "idps_elderly_women", "idps_elderly_men", "idps_total",
        "returnees_girls", "returnees_boys", "returnees_women", "returnees_men", "returnees_elderly_women", "returnees_elderly_men", "returnees_total",
        "host_girls", "host_boys", "host_women", "host_men", "host_elderly_women", "host_elderly_men", "host_total"
    ]
    
    # Slice the dataframe to skip the first two header rows
    data_df = df.iloc[2:].copy()
    data_df.columns = clean_headers
    
    # Filter out HDX tag rows (rows starting with #)
    data_df = data_df[~data_df["state"].astype(str).str.strip().str.startswith("#")]
    
    # Convert numeric columns to numeric types
    num_cols = clean_headers[4:]
    for col in num_cols:
        data_df[col] = pd.to_numeric(data_df[col], errors='coerce').fillna(0).astype(int)
        
    # Calculate school-age (children/youth) populations (Girls + Boys)
    data_df["school_age_girls"] = data_df["idps_girls"] + data_df["returnees_girls"] + data_df["host_girls"]
    data_df["school_age_boys"] = data_df["idps_boys"] + data_df["returnees_boys"] + data_df["host_boys"]
    data_df["school_age_total"] = data_df["school_age_girls"] + data_df["school_age_boys"]
    
    # Keep only relevant columns for school-age population
    cols_to_save = [
        "state", "state_pcode", "lga", "pcode",
        "idps_girls", "idps_boys",
        "returnees_girls", "returnees_boys",
        "host_girls", "host_boys",
        "school_age_girls", "school_age_boys", "school_age_total"
    ]
    
    out_df = data_df[cols_to_save].copy()
    
    # Sort by state then LGA
    out_df = out_df.sort_values(by=["state", "lga"])
    
    # Save to CSV
    out_df.to_csv(out_csv, index=False)
    print(f"Processed and saved school-age population data to {out_csv}")
    print(f"Total LGAs processed: {len(out_df)}")
    print(f"Total School-Age Population (Girls & Boys): {out_df['school_age_total'].sum():,}")
    
    # Print sample LGA values
    print("\nSample LGA School-Age Population Details:")
    print(out_df[["state", "lga", "school_age_girls", "school_age_boys", "school_age_total"]].head(10).to_string(index=False))

if __name__ == "__main__":
    process_sadd()
