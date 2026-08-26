import cv2, pytesseract, os, re
import pandas as pd

tess_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tess_path):
    pytesseract.pytesseract.tesseract_cmd = tess_path

def test_ocr_precision(img_path):
    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    # Preprocessing: convert to grayscale and upscale 2x
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

    # Apply unsharp mask filter to sharpen text edges
    gaussian = cv2.GaussianBlur(gray, (0, 0), 3)
    sharpened = cv2.addWeighted(gray, 1.5, gaussian, -0.5, 0)

    # OTSU threshold
    _, thresh = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    ocr_text = pytesseract.image_to_string(thresh, config='--psm 6')
    lines = [l.strip() for l in ocr_text.split('\n') if l.strip()]

    print(f"File: {img_path} -> Total Lines: {len(lines)}")
    print("=== OCR RAW LINES ===")
    for idx, l in enumerate(lines):
        print(f"{idx:2d}: {l}")

if __name__ == "__main__":
    img_path = r'C:\Users\ranau\.gemini\antigravity\brain\1851bd3e-5323-4ac9-9caa-883050946904\media__1787744809113.jpg'
    test_ocr_precision(img_path)
