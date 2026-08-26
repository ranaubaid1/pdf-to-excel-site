import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import _build_styled_excel_file, _extract_tables_via_text

def test_styled_excel_building():
    pdf_path = "Amna Kashif Mzn.pdf"
    if not os.path.exists(pdf_path):
        print(f"Skipping test, file not found: {pdf_path}")
        return

    with open(pdf_path, "rb") as f:
        dfs = _extract_tables_via_text(f)

    if dfs:
        excel_bytes = _build_styled_excel_file(dfs)
        print(f"Successfully generated styled Excel file ({len(excel_bytes.getvalue())} bytes)")

if __name__ == "__main__":
    test_styled_excel_building()
