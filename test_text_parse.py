import os
import pdfplumber
import re

target_pdf = "1784188747130.pdf"
if not os.path.exists(target_pdf):
    print(f"Skipping test_text_parse.py: {target_pdf} not found in workspace.")
else:
    with pdfplumber.open(target_pdf) as pdf:
        date_pattern = re.compile(r'^\d{2}\s+\w{3}\s+\d{4}\s+')
        amount_pattern = re.compile(r'([+-]\s*PKR[\d,]+\.?\d*|PKR[\d,]+\.?\d*)')
        
        all_entries = []
        
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text:
                continue
            lines = text.split('\n')
            
            current_entry = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if date_pattern.match(line):
                    if current_entry:
                        all_entries.append(current_entry)
                    
                    date_match = re.match(r'(\d{2}\s+\w{3}\s+\d{4})\s+(.*)', line)
                    if date_match:
                        date = date_match.group(1)
                        rest = date_match.group(2)
                        
                        amounts = amount_pattern.findall(rest)
                        desc = amount_pattern.sub('', rest).strip()
                        desc = re.sub(r'\s{2,}', ' ', desc).strip()
                        
                        current_entry = {
                            'date': date,
                            'desc': desc,
                            'amounts': amounts,
                            'page': page_num
                        }
                elif current_entry:
                    amounts_in_line = amount_pattern.findall(line)
                    desc_part = amount_pattern.sub('', line).strip()
                    desc_part = re.sub(r'\s{2,}', ' ', desc_part).strip()
                    
                    if desc_part and desc_part not in ("Account Statement", "Booking Date", "Description", "Credit", "Debit", "Available Balance"):
                        current_entry['desc'] += " " + desc_part
                    current_entry['amounts'].extend(amounts_in_line)
                    
            if current_entry:
                all_entries.append(current_entry)

    print(f"Total entries parsed: {len(all_entries)}")
    for i, e in enumerate(all_entries[:10], 1):
        print(f"Entry {i}: Date={e['date']} | Page={e['page']} | Amounts={e['amounts']}")
        print(f"  Desc: {e['desc']}")
