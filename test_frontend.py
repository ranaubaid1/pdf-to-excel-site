import os
import sys
import time
from playwright.sync_api import sync_playwright

def run_frontend_tests():
    print("\n--- Running Frontend UX Tests ---")
    
    with sync_playwright() as p:
        # Launch browser (headless=True for background running)
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as e:
            print(f"Error launching browser: {e}")
            print("Trying to install Playwright browser binaries...")
            os.system("python -m playwright install chromium")
            try:
                browser = p.chromium.launch(headless=True)
            except Exception as e2:
                print(f"Could not launch browser even after install: {e2}")
                return False

        page = browser.new_page()
        
        # 1. Navigate to http://localhost:8000
        try:
            page.goto("http://localhost:8000", timeout=5000)
            print("1. Navigated to http://localhost:8000 successfully.")
        except Exception as e:
            print(f"Fail: Could not load frontend. Server running? Error: {e}")
            browser.close()
            return False

        # Verify page title
        title = page.title()
        print(f"Page Title: {title}")
        if "TabularX" not in title:
            print("Fail: Title does not match")
            browser.close()
            return False

        # 2. Select happy_path.pdf
        happy_path = os.path.abspath("test_files/happy_path.pdf")
        page.set_input_files("#fileInput", happy_path)
        print("2. Selected happy_path.pdf")
        
        # Check if filebar shows up and convert button is enabled
        filebar_visible = page.locator("#filebar").is_visible()
        convert_enabled = page.locator("#convertBtn").is_enabled()
        print(f"   Filebar visible: {filebar_visible}, Convert button enabled: {convert_enabled}")
        if not filebar_visible or not convert_enabled:
            print("Fail: Filebar not visible or Convert button not enabled after selecting file")
            browser.close()
            return False

        # 3. Click 'x' button (#clearFile) to remove file
        page.locator("#clearFile").click()
        print("3. Clicked clear ('x') button")
        
        # Confirm filebar hides and convert button disables
        filebar_visible = page.locator("#filebar").is_visible()
        convert_enabled = page.locator("#convertBtn").is_enabled()
        print(f"   Filebar visible: {filebar_visible}, Convert button enabled: {convert_enabled}")
        if filebar_visible or convert_enabled:
            print("Fail: Filebar is still visible or Convert button is still enabled after clearing file")
            browser.close()
            return False

        # 4. Select happy_path.pdf again and convert
        page.set_input_files("#fileInput", happy_path)
        
        # We expect a download when we click Convert
        print("4. Clicking 'Convert to Excel' and expecting download...")
        with page.expect_download() as download_info:
            page.locator("#convertBtn").click()
            
            # Immediately check if button disables and shows "Converting…"
            # Note: Because the click is async, we do a quick check
            btn_text = page.locator("#convertBtn").text_content()
            btn_enabled = page.locator("#convertBtn").is_enabled()
            print(f"   Conversion started. Button text: '{btn_text}', Button enabled: {btn_enabled}")
            
        download = download_info.value
        download_path = "test_files/downloaded_happy_path.xlsx"
        download.save_as(download_path)
        print(f"5. File downloaded successfully to: {download_path}")
        
        # Verify success status message
        status_class = page.locator("#status").get_attribute("class")
        status_text = page.locator("#status").text_content()
        print(f"   Status class: {status_class}")
        print(f"   Status text: {status_text}")
        if "success" not in status_class or "Done" not in status_text:
            print("Fail: Success status styling/message incorrect")
            browser.close()
            return False

        # 6. Upload no_table.pdf and check backend error
        no_table_path = os.path.abspath("test_files/no_table.pdf")
        page.set_input_files("#fileInput", no_table_path)
        print("6. Selected no_table.pdf and clicking Convert...")
        page.locator("#convertBtn").click()
        
        # Wait for status to show error class (since it's an async backend call)
        # We can wait for the status element to contain error class
        page.wait_for_selector("#status.error", timeout=5000)
        status_class = page.locator("#status").get_attribute("class")
        status_text = page.locator("#status").text_content()
        print(f"   Status class: {status_class}")
        print(f"   Status text: {status_text}")
        if "error" not in status_class or "No tables found in this PDF" not in status_text:
            print("Fail: Error status styling/message incorrect for no_table.pdf")
            browser.close()
            return False

        # 7. Upload wrong_type.docx (frontend error)
        docx_path = os.path.abspath("test_files/wrong_type.docx")
        print("7. Selecting wrong_type.docx...")
        page.set_input_files("#fileInput", docx_path)
        
        status_class = page.locator("#status").get_attribute("class")
        status_text = page.locator("#status").text_content()
        convert_enabled = page.locator("#convertBtn").is_enabled()
        print(f"   Status class: {status_class}")
        print(f"   Status text: {status_text}")
        print(f"   Convert button enabled: {convert_enabled}")
        
        if "error" not in status_class or "Only .pdf files are supported" not in status_text or convert_enabled:
            print("Fail: Frontend wrong file type validation failed")
            browser.close()
            return False

        print("--- Frontend UX Tests PASSED ---")
        browser.close()
        return True

if __name__ == "__main__":
    success = run_frontend_tests()
    sys.exit(0 if success else 1)
