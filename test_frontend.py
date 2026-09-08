import os
import sys
import time
from playwright.sync_api import sync_playwright

def run_frontend_tests():
    print("\n--- Running STATEXCEL v2.0 Frontend UX Tests ---")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as e:
            print(f"Error launching browser: {e}")
            os.system("python -m playwright install chromium")
            try:
                browser = p.chromium.launch(headless=True)
            except Exception as e2:
                print(f"Could not launch browser: {e2}")
                return False

        page = browser.new_page()
        
        # 1. Navigate to STATEXCEL
        try:
            page.goto("http://localhost:5000", timeout=8000)
            print("1. Navigated to http://localhost:5000 successfully.")
        except Exception as e:
            print(f"Fail: Could not load frontend. Server running on 5000? Error: {e}")
            browser.close()
            return False

        # Verify page title
        title = page.title()
        print(f"Page Title: {title}")
        if "STATEXCEL" not in title:
            print("Fail: Title does not contain STATEXCEL")
            browser.close()
            return False

        # 2. Select happy_path.pdf
        happy_path = os.path.abspath("test_files/happy_path.pdf")
        page.set_input_files("#fileInput", happy_path)
        print("2. Selected happy_path.pdf")
        
        # Check if filebar shows up and buttons are enabled
        filebar_visible = page.locator("#filebar").is_visible()
        preview_enabled = page.locator("#previewBtn").is_enabled()
        quick_enabled = page.locator("#quickConvertBtn").is_enabled()
        print(f"   Filebar visible: {filebar_visible}, Preview enabled: {preview_enabled}, Quick enabled: {quick_enabled}")
        if not filebar_visible or not preview_enabled:
            print("Fail: Filebar not visible or Preview button not enabled")
            browser.close()
            return False

        # 3. Test Preview & In-Browser Grid
        print("3. Clicking 'Preview & Edit in Grid'...")
        page.locator("#previewBtn").click()
        
        # Wait for editor section to appear
        page.wait_for_selector("#editorSection.show", timeout=10000)
        print("4. In-Browser Spreadsheet Editor Grid appeared!")

        # Verify table rows
        row_count = page.locator("#tableBody tr").count()
        print(f"   Grid loaded with {row_count} rows.")
        if row_count < 1:
            print("Fail: Grid has no rows")
            browser.close()
            return False

        # Verify Add Row
        page.locator("#addRowBtn").click()
        new_row_count = page.locator("#tableBody tr").count()
        print(f"   After Add Row: {new_row_count} rows.")
        if new_row_count != row_count + 1:
            print("Fail: Add row did not increase count")
            browser.close()
            return False

        # Verify Swap Columns
        page.locator("#swapColsBtn").click()
        print("   Clicked Swap Debit/Credit successfully.")

        # 5. Test Export XLSX from Grid
        print("5. Clicking Export Excel from Grid and expecting download...")
        with page.expect_download() as download_info:
            page.locator("#exportXlsxBtn").click()
        
        download = download_info.value
        download_path = "test_files/downloaded_happy_path.xlsx"
        download.save_as(download_path)
        print(f"6. Excel file downloaded successfully: {download_path}")

        # 6. Test Reset / Upload New
        page.locator("#resetEditorBtn").click()
        upload_visible = page.locator("#uploadPanel").is_visible()
        editor_visible = page.locator("#editorSection.show").is_visible()
        print(f"   Upload panel visible: {upload_visible}, Editor visible: {editor_visible}")

        print("--- All STATEXCEL v2.0 Frontend UX Tests PASSED ---")
        browser.close()
        return True

if __name__ == "__main__":
    success = run_frontend_tests()
    sys.exit(0 if success else 1)
