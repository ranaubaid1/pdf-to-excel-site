import os
import io
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def create_happy_path(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    elements.append(Paragraph("Happy Path PDF Table Test", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    
    # Table Data
    data = [
        ["Name", "Age", "City"],
        ["Alice", "28", "New York"],
        ["Bob", "34", "San Francisco"],
        ["Charlie", "22", "Boston"]
    ]
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(t)
    doc.build(elements)
    print(f"Created {filename}")

def create_multi_table(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Page 1, Table 1
    elements.append(Paragraph("Page 1 - Table 1", styles["Heading1"]))
    elements.append(Spacer(1, 10))
    data1 = [
        ["Product", "Price", "Qty"],
        ["Laptop", "999.99", "5"],
        ["Mouse", "24.99", "12"]
    ]
    t1 = Table(data1)
    t1.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black)]))
    elements.append(t1)
    elements.append(Spacer(1, 20))
    
    # Page 1, Table 2
    elements.append(Paragraph("Page 1 - Table 2", styles["Heading1"]))
    elements.append(Spacer(1, 10))
    data2 = [
        ["Task", "Status"],
        ["Design", "Done"],
        ["Code", "Pending"]
    ]
    t2 = Table(data2)
    t2.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black)]))
    elements.append(t2)
    
    # Page Break to Page 2
    elements.append(PageBreak())
    
    # Page 2, Table 1
    elements.append(Paragraph("Page 2 - Table 1", styles["Heading1"]))
    elements.append(Spacer(1, 10))
    data3 = [
        ["Employee", "Role", "Salary"],
        ["Eve", "Manager", "85000"],
        ["Frank", "Developer", "70000"]
    ]
    t3 = Table(data3)
    t3.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black)]))
    elements.append(t3)
    
    doc.build(elements)
    print(f"Created {filename}")

def create_no_table(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("No Table PDF Test", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    
    text = (
        "This is a PDF file that contains plain text only. It has no tables, "
        "no grids, no headers, and no rows. The converter should reject this file "
        "and return a 422 Unprocessable Entity error message stating that no "
        "tables were found in this PDF file."
    )
    elements.append(Paragraph(text, styles["BodyText"]))
    doc.build(elements)
    print(f"Created {filename}")

def create_messy_table(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("Messy Real-World Table Test", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    
    # Cells:
    # row 0: headers
    # row 1: merged cells or empty cells, multi-line text, currency
    # Let's define the cells
    # We will put a Paragraph in one cell for multi-line text
    body_style = styles["BodyText"]
    
    data = [
        ["Header A", "Header B", "Header C", "Header D"],
        ["Row 1 Col A", "", "Row 1 Col C", "$1,234.56"], # Empty cell at col B
        ["Row 2\nLine 2\nLine 3", "Row 2 Col B", "Row 2 Col C", "€ 500,00"], # multi-line
        ["Row 3 Col A", "Row 3 Col B", "Row 3 Col C", "$10,000"]
    ]
    
    # Wait, ReportLab Table doesn't do multi-line string cells automatically unless wrapped in Paragraph 
    # or using \n which works sometimes. Let's wrap multi-line in Paragraph or just use '\n' which reportlab supports in cells if cell is tall.
    # Actually reportlab Table cells support standard strings with '\n' and split them automatically if style aligns, or we can wrap them in Paragraph.
    # Let's wrap the multi-line in Paragraph to be safe:
    multi_paragraph = Paragraph("Row 2<br/>Line 2<br/>Line 3", body_style)
    data[2][0] = multi_paragraph
    
    t = Table(data)
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        # Let's simulate a merged cell. Reportlab TableStyle lets us merge cells using:
        # ('SPAN', (start_col, start_row), (end_col, end_row))
        # Let's merge row 3, col B and col C
        ('SPAN', (1, 3), (2, 3)),
    ]))
    elements.append(t)
    doc.build(elements)
    print(f"Created {filename}")

def create_oversized(filename):
    # We need a PDF > 20MB. 
    # Instead of generating a real PDF with pages (which would take too long), we can append trash bytes at the end of a valid PDF structure, 
    # or write a dummy PDF file that is large.
    # Let's write a standard small PDF first, then append large dummy data, or write a script to write large data.
    # Actually, a PDF parsing engine like pdfplumber might read it. But does the server reject it before parsing?
    # Yes! app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
    # This check happens at the Flask request body level! So Flask rejects it automatically based on Content-Length, 
    # even if it's just random bytes or a padded PDF.
    # Let's create a valid happy_path PDF first, then write it to a file, and then pad it with 21MB of null bytes or comments.
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Oversized PDF Test", styles["Heading1"])]
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    
    with open(filename, "wb") as f:
        f.write(pdf_bytes)
        # Pad with 21MB of zeros or whitespace
        f.write(b" " * (21 * 1024 * 1024))
    print(f"Created {filename} (size: {os.path.getsize(filename) / (1024*1024):.2f} MB)")

def create_corrupt(filename):
    # Truncated PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Corrupt PDF Test", styles["Heading1"])]
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    
    # Truncate it to half length
    truncated_bytes = pdf_bytes[:len(pdf_bytes)//2]
    with open(filename, "wb") as f:
        f.write(truncated_bytes)
    print(f"Created {filename}")

def create_zero_byte(filename):
    with open(filename, "wb") as f:
        pass
    print(f"Created {filename}")

def create_wrong_types():
    # wrong extension files
    with open("wrong_type.docx", "w") as f:
        f.write("This is a Word document dummy.")
    with open("wrong_type.txt", "w") as f:
        f.write("This is a plain text file.")
    with open("wrong_type.png", "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRdummy")
    
    # content mismatch (txt renamed to pdf)
    with open("mismatch_content.pdf", "w") as f:
        f.write("This is a plain text file renamed to pdf.")
    print("Created wrong type files.")

if __name__ == "__main__":
    os.makedirs("test_files", exist_ok=True)
    os.chdir("test_files")
    create_happy_path("happy_path.pdf")
    create_multi_table("multi_table.pdf")
    create_no_table("no_table.pdf")
    create_messy_table("messy_table.pdf")
    create_oversized("oversized.pdf")
    create_corrupt("corrupt.pdf")
    create_zero_byte("zero_byte.pdf")
    create_wrong_types()
