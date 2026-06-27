import pandas as pd

def check_categories():
    df = pd.read_csv("/workspaces/NigeriaBAY/data/clean/IDP.csv")
    print("Unique population categories:")
    print(df["Population Category"].value_counts(dropna=False))
    print("\nSample population columns for each category:")
    print(df.groupby("Population Category")[["Households", "Individuals"]].sum())

if __name__ == "__main__":
    check_categories()
