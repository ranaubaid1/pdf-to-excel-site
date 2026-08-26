import os
import io
import requests
import pandas as pd

def test_file_conversion(file_path):
    if not os.path.exists(file_path):
        print(f"Skipping missing test file: {file_path}")
        return

    print(f"\n=== Testing {file_path} ===")
    with open(file_path, "rb") as f:
        res = requests.post("http://localhost:5000/api/convert", files={"file": f})

    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        xl = pd.ExcelFile(io.BytesIO(res.content))
        print(f"Sheets: {xl.sheet_names}")
        for sheet in xl.sheet_names:
            df = xl.parse(sheet, header=None)
            print(f"\n--- Sheet: {sheet} ({len(df)} rows, {len(df.columns)} cols) ---")
            print("First 15 rows:")
            print(df.head(15).to_string())
            print(f"\nLast 10 rows:")
            print(df.tail(10).to_string())
    else:
        print(f"Error: {res.text}")

if __name__ == "__main__":
    test_file_conversion("Amna Kashif Mzn.pdf")
    test_file_conversion("1784188747130.pdf")

    if os.path.exists("Amna_Kashif_Meezan_Statement.xlsx"):
        print("\n\n=== REFERENCE Excel ===")
        xl_ref = pd.ExcelFile("Amna_Kashif_Meezan_Statement.xlsx")
        for sheet in xl_ref.sheet_names:
            df_ref = xl_ref.parse(sheet, header=None)
            print(f"Sheet: {sheet} ({len(df_ref)} rows, {len(df_ref.columns)} cols)")
            print("First 15 rows:")
            print(df_ref.head(15).to_string())
