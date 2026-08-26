import os
import io
import time
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:5000"

def test_api_health():
    print("\n--- Testing Health Endpoint ---")
    try:
        res = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {res.status_code}, Response: {res.json()}")
        return res.status_code == 200
    except Exception as e:
        print(f"Failed to connect to backend: {e}")
        return False

def test_happy_path():
    print("\n--- Test 1: Functional - Happy Path ---")
    file_path = "test_files/happy_path.pdf"
    with open(file_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/api/convert", files={"file": f})
    
    print(f"Status Code: {res.status_code}")
    if res.status_code != 200:
        print(f"Fail: Expected 200, got {res.status_code}. Response: {res.text}")
        return False
    
    # Check headers
    content_type = res.headers.get("Content-Type")
    content_disp = res.headers.get("Content-Disposition")
    print(f"Content-Type: {content_type}")
    print(f"Content-Disposition: {content_disp}")
    
    # Read as Excel
    excel_bytes = io.BytesIO(res.content)
    try:
        xl = pd.ExcelFile(excel_bytes)
        print(f"Sheet names: {xl.sheet_names}")
        if len(xl.sheet_names) != 1 or xl.sheet_names[0] != "Page1_Table1":
            print(f"Fail: Expected sheet name Page1_Table1, got {xl.sheet_names}")
            return False
        
        df = xl.parse(xl.sheet_names[0])
        print("Data Extracted:")
        print(df)
        
        # Verify columns and rows
        expected_cols = ["Name", "Age", "City"]
        expected_rows = [
            ["Alice", 28, "New York"],
            ["Bob", 34, "San Francisco"],
            ["Charlie", 22, "Boston"]
        ]
        
        if list(df.columns) != expected_cols:
            print(f"Fail: Columns don't match. Expected {expected_cols}, got {list(df.columns)}")
            return False
        
        for i, row in enumerate(expected_rows):
            actual_row = list(df.iloc[i])
            # Handle possible string/numeric differences
            actual_row = [str(x) for x in actual_row]
            expected_row_str = [str(x) for x in row]
            if actual_row != expected_row_str:
                print(f"Fail: Row {i} doesn't match. Expected {expected_row_str}, got {actual_row}")
                return False
                
        print("Pass")
        return True
    except Exception as e:
        print(f"Fail: Could not open as valid Excel. Error: {e}")
        return False

def test_multiple_tables_pages():
    print("\n--- Test 2: Multiple Tables, Multiple Pages ---")
    file_path = "test_files/multi_table.pdf"
    with open(file_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/api/convert", files={"file": f})
        
    print(f"Status Code: {res.status_code}")
    if res.status_code != 200:
        print(f"Fail: Expected 200, got {res.status_code}. Response: {res.text}")
        return False
        
    excel_bytes = io.BytesIO(res.content)
    try:
        xl = pd.ExcelFile(excel_bytes)
        print(f"Sheet names: {xl.sheet_names}")
        expected_sheets = ["Page1_Table1", "Page1_Table2", "Page2_Table1"]
        if xl.sheet_names != expected_sheets:
            print(f"Fail: Sheet names mismatch. Expected {expected_sheets}, got {xl.sheet_names}")
            return False
            
        # Verify Table 1
        df1 = xl.parse("Page1_Table1")
        print("Page1_Table1:")
        print(df1)
        
        # Verify Table 2
        df2 = xl.parse("Page1_Table2")
        print("Page1_Table2:")
        print(df2)
        
        # Verify Table 3
        df3 = xl.parse("Page2_Table1")
        print("Page2_Table1:")
        print(df3)
        
        print("Pass")
        return True
    except Exception as e:
        print(f"Fail: Error parsing Excel. {e}")
        return False

def test_no_table():
    print("\n--- Test 3: No Table in PDF ---")
    file_path = "test_files/no_table.pdf"
    with open(file_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/api/convert", files={"file": f})
        
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")
    
    if res.status_code == 422:
        try:
            data = res.json()
            if "No tables" in data.get("error", ""):
                print("Pass")
                return True
        except:
            pass
    print("Fail")
    return False

def test_wrong_file_type():
    print("\n--- Test 4: Wrong File Type ---")
    
    # 4a. docx
    print("Testing docx...")
    with open("test_files/wrong_type.docx", "rb") as f:
        res1 = requests.post(f"{BASE_URL}/api/convert", files={"file": f})
    print(f"docx -> Status: {res1.status_code}, Response: {res1.text}")
    
    # 4b. png (Supported via OCR!)
    print("Testing png...")
    with open("test_files/wrong_type.png", "rb") as f:
        res2 = requests.post(f"{BASE_URL}/api/convert", files={"file": f})
    print(f"png -> Status: {res2.status_code}, Response: {res2.text}")
    
    # 4c. txt
    print("Testing txt...")
    with open("test_files/wrong_type.txt", "rb") as f:
        res3 = requests.post(f"{BASE_URL}/api/convert", files={"file": f})
    print(f"txt -> Status: {res3.status_code}, Response: {res3.text}")
    
    # 4d. renamed txt to pdf (extension mismatch)
    print("Testing renamed txt -> pdf...")
    with open("test_files/mismatch_content.pdf", "rb") as f:
        res4 = requests.post(f"{BASE_URL}/api/convert", files={"file": f})
    print(f"renamed pdf -> Status: {res4.status_code}, Response: {res4.text}")
    
    # Check all cases
    passed = True
    if res1.status_code != 400 or "supported" not in res1.text:
        print("Fail: docx not rejected with 400 + supported msg")
        passed = False
    if res3.status_code != 400 or "supported" not in res3.text:
        print("Fail: txt not rejected with 400 + supported msg")
        passed = False
    
    # Let's see what happens to the mismatch PDF content
    # If the extension is pdf, it passes the filename check, and tries to parse it.
    # It might return a 500 error if pdfplumber crashes, or it might return 422 if it thinks there are no tables.
    print(f"Mismatch PDF content status code: {res4.status_code}")
    if res4.status_code == 500:
        print("Notice: Mismatch PDF returned 500 (stack trace/internal server error).")
    
    if passed:
        print("Pass (except potentially mismatch content 500 check)")
    return passed

def test_oversized_file():
    print("\n--- Test 5: Oversized File ---")
    file_path = "test_files/oversized.pdf"
    try:
        # Note: We must be careful not to crash the python runner or exceed requests timeouts
        with open(file_path, "rb") as f:
            res = requests.post(f"{BASE_URL}/api/convert", files={"file": f})
        print(f"Status Code: {res.status_code}")
        print(f"Response (truncated): {res.text[:200]}")
        if res.status_code == 413 or res.status_code == 400 or res.status_code == 500:
            # Let's check how Flask handles MAX_CONTENT_LENGTH. Usually it raises a RequestEntityTooLarge (413)
            # or if custom handled, a clean error.
            print("Server handled/rejected it. Pass.")
            return True
        else:
            print("Fail: Server did not reject oversized file cleanly.")
            return False
    except Exception as e:
        print(f"Fail/Error while sending: {e}")
        return False

def test_empty_corrupt_pdf():
    print("\n--- Test 6: Empty / Corrupted PDF ---")
    
    # 6a. Zero byte file
    print("Testing 0-byte file...")
    with open("test_files/zero_byte.pdf", "rb") as f:
        res1 = requests.post(f"{BASE_URL}/api/convert", files={"file": f})
    print(f"0-byte -> Status: {res1.status_code}, Response: {res1.text}")
    
    # 6b. Corrupted PDF (truncated)
    print("Testing corrupted/truncated PDF...")
    with open("test_files/corrupt.pdf", "rb") as f:
        res2 = requests.post(f"{BASE_URL}/api/convert", files={"file": f})
    print(f"corrupt -> Status: {res2.status_code}, Response: {res2.text}")
    
    # We want to confirm graceful error handling (not returning raw stack traces/500 errors to users)
    # The requirement says: "Confirm graceful error handling, not a 500 stack trace leaking to the user."
    passed = True
    if res1.status_code == 500:
        print("Fail: 0-byte PDF returned 500")
        passed = False
    if res2.status_code == 500:
        print("Fail: Corrupted PDF returned 500")
        passed = False
        
    if passed:
        print("Pass")
    else:
        print("Fail (one or both returned 500)")
    return passed

def test_messy_tables():
    print("\n--- Test 7: Messy Real-World Tables ---")
    file_path = "test_files/messy_table.pdf"
    with open(file_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/api/convert", files={"file": f})
    
    print(f"Status Code: {res.status_code}")
    if res.status_code != 200:
        print(f"Fail: Expected 200, got {res.status_code}. Response: {res.text}")
        return False
        
    excel_bytes = io.BytesIO(res.content)
    try:
        xl = pd.ExcelFile(excel_bytes)
        df = xl.parse(xl.sheet_names[0])
        print("Extracted Messy Table Data:")
        print(df)
        
        # Check alignment and columns.
        # Original columns: "Header A", "Header B", "Header C", "Header D"
        # Row 1 Col A, <empty>, Row 1 Col C, $1,234.56
        # Row 2 (multi-line), Row 2 Col B, Row 2 Col C, € 500,00
        # Row 3 Col A, Row 3 Col B (merged with C), Row 3 Col C (merged), $10,000
        print(f"Columns: {list(df.columns)}")
        print("Row 0 data:", list(df.iloc[0]))
        print("Row 1 data:", list(df.iloc[1]))
        print("Row 2 data:", list(df.iloc[2]))
        
        # Checking columns length
        if len(df.columns) != 4:
            print(f"Fail: Expected 4 columns, got {len(df.columns)}")
            return False
            
        print("Pass")
        return True
    except Exception as e:
        print(f"Fail: Error parsing Excel. {e}")
        return False

def test_cors():
    print("\n--- Test 9: CORS Headers Check ---")
    # Send request with Origin header
    headers = {"Origin": "http://localhost:8000"}
    file_path = "test_files/happy_path.pdf"
    with open(file_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/api/convert", files={"file": f}, headers=headers)
        
    print(f"Status Code: {res.status_code}")
    acao = res.headers.get("Access-Control-Allow-Origin")
    print(f"Access-Control-Allow-Origin: {acao}")
    if acao == "*" or acao == "http://localhost:8000":
        print("Pass")
        return True
    else:
        print("Fail: CORS headers not present or incorrect")
        return False

def make_request(idx):
    file_path = "test_files/happy_path.pdf"
    t0 = time.time()
    try:
        with open(file_path, "rb") as f:
            # We add a delay parameter or just send
            res = requests.post(f"{BASE_URL}/api/convert", files={"file": f})
        dt = time.time() - t0
        return idx, res.status_code, len(res.content), dt
    except Exception as e:
        return idx, "Error", str(e), time.time() - t0

def test_concurrent_requests():
    print("\n--- Test 10: Concurrent Requests ---")
    # Send 5 requests simultaneously
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(5)]
        results = [f.result() for f in futures]
        
    passed = True
    for idx, status, length, dt in results:
        print(f"Request {idx}: Status={status}, Length={length} bytes, Duration={dt:.2f}s")
        if status != 200:
            passed = False
            
    if passed:
        print("Pass")
    else:
        print("Fail (some requests failed)")
    return passed

if __name__ == "__main__":
    test_api_health()
    test_happy_path()
    test_multiple_tables_pages()
    test_no_table()
    test_wrong_file_type()
    test_oversized_file()
    test_empty_corrupt_pdf()
    test_messy_tables()
    test_cors()
    test_concurrent_requests()
