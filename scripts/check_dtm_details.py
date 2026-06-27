import pandas as pd

def check_dtm_cols():
    df = pd.read_csv("/workspaces/NigeriaBAY/data/clean/IDP.csv", nrows=5)
    print("All Columns in IDP.csv:")
    cols = df.columns.tolist()
    for idx, c in enumerate(cols):
        print(f"Col {idx}: {c}")

if __name__ == "__main__":
    check_dtm_cols()
