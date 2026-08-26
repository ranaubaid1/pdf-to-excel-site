# TabularX — PDF to Excel Converter

A full website: a Flask backend that extracts tables from PDFs and returns an
`.xlsx` file, plus a frontend page to upload/download.

## Project structure

```
pdf-to-excel-site/
├── backend/
│   ├── app.py            # Flask API (POST /api/convert)
│   └── requirements.txt
├── frontend/
│   └── index.html        # Upload UI (open directly in a browser)
└── README.md
```

## 1. Run the backend

```bash
cd backend
pip install -r requirements.txt
python3 app.py
```

This starts the API at `http://localhost:5000`.
Health check: `GET http://localhost:5000/api/health`

## 2. Run the frontend

Just open `frontend/index.html` in your browser (double-click it, or use
`Live Server` in VS Code). It's a static page — no build step needed.

If your backend runs somewhere other than `http://localhost:5000`, update
the `API_BASE` constant near the top of the `<script>` tag in `index.html`.

## How it works

1. User uploads a PDF on the frontend.
2. Frontend sends it as `multipart/form-data` to `POST /api/convert`.
3. Backend uses `pdfplumber` to detect and extract every table on every page.
4. Each table becomes one sheet (`Page1_Table1`, `Page1_Table2`, ...) in an
   Excel workbook, built with `pandas` + `openpyxl`.
5. The `.xlsx` file is streamed back and the browser downloads it.

## Notes / next steps if you want to deploy this for real

- **Hosting**: deploy `backend/` to something like Render, Railway, or a VPS
  (it's a plain Flask app — `gunicorn app:app` for production). Host
  `frontend/index.html` on Netlify/Vercel/GitHub Pages, or serve it from
  Flask itself with `send_from_directory`.
- **File size limit**: currently capped at 20MB (`MAX_CONTENT_LENGTH` in
  `app.py`) — adjust as needed.
- **Scanned PDFs**: this only works for PDFs with real text/table structure.
  Scanned/image-only PDFs would need OCR (e.g. `pytesseract`) added first.
- **Security**: add rate-limiting and a stricter CORS origin list
  (`CORS(app, origins=["https://yourdomain.com"])`) before going live.
