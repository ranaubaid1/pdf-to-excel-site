import cv2, pytesseract, os, re
import pandas as pd

tess_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tess_path):
    pytesseract.pytesseract.tesseract_cmd = tess_path

def test_ocr_date_normalization(img_path):
    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    # Preprocessing with unsharp mask sharpening
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
    gaussian = cv2.GaussianBlur(gray, (0, 0), 3)
    sharpened = cv2.addWeighted(gray, 1.5, gaussian, -0.5, 0)
    _, thresh = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    ocr_text = pytesseract.image_to_string(thresh, config='--psm 6')
    lines = [l.strip() for l in ocr_text.split('\n') if l.strip()]

    # Date pattern matching DD/MM/YYYY or DDMM/YYYY or DD Mon YYYY
    date_pattern = re.compile(r'^(?:\d{2}[/\-\s](?:\d{2}|\w{3})[/\-\s]\d{4}|\d{4}[/\-\s]\d{4})\b')
    amount_pattern = re.compile(r'(?:[+-]\s*PKR\s*[\d,.]+|PKR\s*[\d,.]+|(?<=\s)[\d,]+\.\d{2}(?=\s|$)|(?<=\s)[\d,]+\.\d{1,2}(?=\s|$))')

    entries = []
    current = None

    for line in lines:
        # Normalize missing slash in dates like 0201/2026 -> 02/01/2026
        norm_line = re.sub(r'^(\d{2})(\d{2})/(\d{4})', r'\1/\2/\3', line)
        if date_pattern.match(norm_line):
            if current:
                entries.append(current)

            m = re.match(r'^(\d{2}[/\-\s](?:\d{2}|\w{3})[/\-\s]\d{4})(?:\s+(\d{2}[/\-\s](?:\d{2}|\w{3})[/\-\s]\d{4}))?\s+(.*)', norm_line)
            if m:
                tx_date = m.group(1)
                rest = m.group(3)
                amounts = amount_pattern.findall(rest)
                desc = amount_pattern.sub('', rest).strip()
                current = {'date': tx_date, 'desc': desc, 'amounts': amounts}
        elif current:
            amts = amount_pattern.findall(line)
            desc_part = amount_pattern.sub('', line).strip()
            if desc_part and not desc_part.startswith('This is a system'):
                current['desc'] += ' ' + desc_part
            current['amounts'].extend(amts)

    if current:
        entries.append(current)

    print(f"File: {img_path} -> Parsed entries: {len(entries)}")
    for idx, e in enumerate(entries, 1):
        print(f"Row {idx:2d}: Date={e['date']} | Desc={e['desc'][:40]:40s} | Amounts={e['amounts']}")

if __name__ == "__main__":
    img_path = r'C:\Users\ranau\.gemini\antigravity\brain\1851bd3e-5323-4ac9-9caa-883050946904\media__1787744809113.jpg'
    test_ocr_date_normalization(img_path)
