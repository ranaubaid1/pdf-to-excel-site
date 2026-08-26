import os
import sys

# Add root folder to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import _extract_tables_via_text

def test_allied_statement_parsing(pdf_path="C:/Users/ranau/Downloads/Amna Kashif Allied.pdf"):
    if not os.path.exists(pdf_path):
        print(f"Skipping test, PDF file not found at: {pdf_path}")
        return

    with open(pdf_path, "rb") as f:
        dfs = _extract_tables_via_text(f)

    if dfs and len(dfs) > 0:
        df = dfs[0]
        records = df.attrs.get("records", [])
        meta = df.attrs.get("metadata", {})
        
        print(f"File: {pdf_path}")
        print(f"Bank Name: {df.attrs.get('bank_name')}")
        print(f"Account Title: {meta.get('account_title')}")
        print(f"Account Number: {meta.get('account_number')}")
        print(f"Total Transactions Parsed: {len(records)}")

        total_debit = sum(r["debit"] for r in records if r.get("debit") is not None)
        total_credit = sum(r["credit"] for r in records if r.get("credit") is not None)
        print(f"Total Debit:  {total_debit:,.2f}")
        print(f"Total Credit: {total_credit:,.2f}")
    else:
        print("No tables extracted.")

if __name__ == "__main__":
    test_allied_statement_parsing()
