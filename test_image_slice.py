import cv2, pytesseract, os, re
import pandas as pd

tess_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tess_path):
    pytesseract.pytesseract.tesseract_cmd = tess_path

def test_sliced_ocr(img_path):
    img = cv2.imread(img_path)
    h, w = img.shape[:2]
    aspect_ratio = h / float(w)
    
    # Determine page slices
    num_pages = max(1, int(round(aspect_ratio / 1.2)))
    print(f"Image Aspect Ratio: {aspect_ratio:.2f} -> Slicing into {num_pages} pages")

    slice_h = h // num_pages
    lines = []

    for p in range(num_pages):
        y1 = p * slice_h
        y2 = (p + 1) * slice_h if p < num_pages - 1 else h
        crop = img[y1:y2, 0:w]

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        cw = crop.shape[1]
        if cw < 1600:
            scale = 1600 / float(cw)
            gray = cv2.resize(gray, (int(cw * scale), int(gray.shape[0] * scale)), interpolation=cv2.INTER_CUBIC)

        ocr_t = pytesseract.image_to_string(gray, config='--psm 6')
        page_lines = [l.strip() for l in ocr_t.split('\n') if l.strip()]
        print(f"\n--- SLICE {p+1}/{num_pages} ({len(page_lines)} lines) ---")
        for l in page_lines[:10]:
            print("  ", l)
        lines.extend(page_lines)

    return lines

if __name__ == "__main__":
    img_path = r'C:\Users\ranau\.gemini\antigravity\brain\1851bd3e-5323-4ac9-9caa-883050946904\media__1787744809113.jpg'
    test_sliced_ocr(img_path)
