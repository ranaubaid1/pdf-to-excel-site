import pytesseract
from PIL import Image, ImageDraw, ImageFont
import os
import io

# Set Tesseract binary path on Windows
tess_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tess_path):
    pytesseract.pytesseract.tesseract_cmd = tess_path

def test_ocr_on_sample_image():
    # Create a synthetic image of a bank statement table
    img = Image.new('RGB', (1000, 600), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Header metadata
    d.text((50, 30), "Meezan Bank Account Statement", fill=(0, 0, 0))
    d.text((50, 60), "Account Title: AMNA KASHIF", fill=(0, 0, 0))
    d.text((50, 80), "Account Number: 02660103760430", fill=(0, 0, 0))
    d.text((50, 100), "IBAN: PK31MEZN0002660103760430", fill=(0, 0, 0))
    d.text((50, 120), "Opening Balance: 1,844,447.66", fill=(0, 0, 0))
    d.text((50, 140), "Closing Balance: 496,730.24", fill=(0, 0, 0))

    # Table Header
    d.text((50, 180), "Booking Date    Description                                Credit           Debit          Available Balance", fill=(0, 0, 0))
    
    # Rows
    d.text((50, 220), "03 Jul 2025    Encashment of Instrument PO.0245.2151252    + PKR10,000,000.00             PKR11,844,447.66", fill=(0, 0, 0))
    d.text((50, 260), "04 Jul 2025    FED Deduction AC-PL52714                                     - PKR32.00    PKR11,844,415.66", fill=(0, 0, 0))
    d.text((50, 300), "05 Jul 2025    ATM Cash Withdrawal 1LINK                                    - PKR20,000.00  PKR11,824,415.66", fill=(0, 0, 0))

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Perform OCR
    text = pytesseract.image_to_string(Image.open(img_bytes))
    print("=== OCR EXTRACTED TEXT ===")
    print(text)

if __name__ == "__main__":
    test_ocr_on_sample_image()
