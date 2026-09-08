# STATEXCEL — Bank Statement to Excel Converter (v2.0 Pro)

> **High-Precision Bank Statement & Document Converter for Accountants, Financial Analysts, Bookkeepers, and Business Owners.**

STATEXCEL is a full-stack financial data conversion suite that transforms native PDF, scanned PDF, Microsoft Word (`.docx`), and document images into clean, structured Excel (`.xlsx`) workbooks and CSV files with **100% transaction integrity**, in-browser spreadsheet grid editing, and automatic balance reconciliation.

---

## 🌟 Key Features

- 🏦 **Bank-Universal Statement Engine**: Specialized parsing for global bank formats (Meezan, Bank of Punjab, Allied Bank, Standard Chartered, Chase, Wells Fargo, Barclays, etc.).
- 👁️ **High-Precision OCR**: Integrated Tesseract + OpenCV image preprocessing to accurately extract tables from scanned PDFs and phone photos.
- 📝 **Word (.docx) & Non-Table Support**: Converts Microsoft Word tables and non-table structured documents with 100% universal fallbacks.
- 🔒 **Password-Protected PDF Support**: Interactive decryption handling for encrypted bank statement downloads.
- 📊 **In-Browser Spreadsheet Grid Editor**: Live interactive spreadsheet interface allowing cell edits, column swapping (Debit ⮂ Credit), row additions/deletions, and instant summary KPI recalculation before downloading.
- 🧮 **Automatic Balance Reconciliation**: Audits opening balance, running transactions, deposits, withdrawals, and closing balances with validation badges.
- 🛡️ **Bank-Grade Security**:
  - In-memory stream processing (files are never stored on disk).
  - Magic-byte file signature validation to block corrupted or disguised binaries.
  - Rate limiting via `Flask-Limiter`.
  - Configurable CORS origin protection.

---

## 📁 Project Structure

```
pdf-to-excel-site/
├── backend/
│   ├── app.py            # Flask API & Data Extraction Engine
│   └── requirements.txt  # Python backend dependencies
├── frontend/
│   └── index.html        # Interactive Fintech UI & Spreadsheet Editor
├── test_files/           # Test fixtures & synthetic generation scripts
├── .env.example          # Environment variables template
├── requirements.txt      # Root dependencies
├── test_backend.py       # Comprehensive API & extraction test suite
├── test_frontend.py      # Playwright end-to-end browser UX tests
├── Dockerfile            # Production container configuration
├── render.yaml           # One-click Render deployment blueprint
└── README.md
```

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- **Python 3.10+**
- **Tesseract-OCR** (Optional, for scanned document OCR):
  - **Windows**: Install via `UB-Mannheim/tesseract/wiki` to `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - **macOS**: `brew install tesseract`
  - **Linux / Ubuntu**: `sudo apt-get install -y tesseract-ocr`

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python backend/app.py
```
The server will start on `http://localhost:5000`. Navigate to `http://localhost:5000` in your web browser to open the STATEXCEL interface.

---

## 🧪 Running Automated Tests

Run the complete backend integration and extraction test suite:
```bash
python -u test_backend.py
```

Run the Playwright browser end-to-end UI tests:
```bash
python test_frontend.py
```

---

## 🌐 API Reference

### 1. Health Check
`GET /api/health`
```json
{
  "status": "healthy",
  "app": "STATEXCEL",
  "version": "2.0.0",
  "docx_support": true,
  "pypdf_support": true,
  "rate_limiting": true,
  "tesseract": true
}
```

### 2. Preview & Parse Statement
`POST /api/preview`
- **Body**: `multipart/form-data` with `file` and optional `password`.
- **Response**: JSON metadata, column definitions, extracted rows, and running totals.

### 3. Export Grid to XLSX / CSV
`POST /api/export`
- **Body**: JSON payload containing edited `sheets`, `format` (`"xlsx"` or `"csv"`), `is_statement`, and `metadata`.
- **Response**: Formatted `.xlsx` spreadsheet or `.csv` download stream.

### 4. Direct 1-Click Convert
`POST /api/convert`
- **Body**: `multipart/form-data` with `file` and optional `password`.
- **Response**: Directly downloads the formatted `.xlsx` workbook.

---

## 🚢 Deployment

### Deploy to Render / Docker
This repository includes a `render.yaml` and `Dockerfile` ready for zero-configuration deployment:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT backend.app:app`

---

## 📄 License
MIT License &bull; Engineered for professional accounting and financial data workflows.
