import pdfplumber
import re
import pandas as pd

def _amount_to_number(amt_str):
    if not amt_str or str(amt_str).strip() == "":
        return None
    num_str = amt_str.replace('+', '').replace('-', '').replace('PKR', '').replace(',', '').replace(' ', '').strip()
    try:
        val = float(num_str)
        if val == 0.0:
            return None # Blank for 0.00
        return val
    except ValueError:
        return None

def parse_bop_statement(pdf_path):
    date_pattern = re.compile(r'^\d{2}[/\-\s](?:\d{2}|\w{3})[/\-\s]\d{4}\b')
    amount_pattern = re.compile(r'(?:[+-]\s*PKR\s*[\d,]+\.?\d*|PKR\s*[\d,]+\.?\d*|(?<=\s)[\d,]+\.\d{2}(?=\s|$))')
    footer_pattern = re.compile(r'^\d+\s*\|\s*Page$|^\*\*\*\*\*\*End of statement\*\*\*\*\*\*')

    all_entries = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text:
                continue
            lines = text.split('\n')
            current_entry = None

            for line in lines:
                line = line.strip()
                if not line or footer_pattern.match(line) or 'This is a system generated report' in line or 'STATEMENT PERIOD' in line:
                    continue

                if date_pattern.match(line):
                    if current_entry:
                        all_entries.append(current_entry)

                    m = re.match(r'^(\d{2}[/\-\s](?:\d{2}|\w{3})[/\-\s]\d{4})(?:\s+(\d{2}[/\-\s](?:\d{2}|\w{3})[/\-\s]\d{4}))?\s+(.*)', line)
                    if m:
                        tx_date = m.group(1)
                        val_date = m.group(2)
                        rest = m.group(3)

                        amounts = amount_pattern.findall(rest)
                        desc = amount_pattern.sub('', rest).strip()
                        desc = re.sub(r'\s{2,}', ' ', desc).strip()

                        current_entry = {
                            'date': tx_date,
                            'val_date': val_date,
                            'desc': desc,
                            'amounts': amounts,
                        }
                elif current_entry:
                    amounts_in_line = amount_pattern.findall(line)
                    desc_part = amount_pattern.sub('', line).strip()
                    desc_part = re.sub(r'\s{2,}', ' ', desc_part).strip()

                    if desc_part and desc_part not in (
                        "Account Statement", "Booking Date", "Description",
                        "Credit", "Debit", "Available Balance", "Balance",
                        "Transaction Value Instrument Cr. Remaining",
                        "Nature of Transaction Dr. Amount",
                        "Date Date Number Amount Balance",
                    ):
                        current_entry['desc'] += ' ' + desc_part
                    current_entry['amounts'].extend(amounts_in_line)

            if current_entry:
                all_entries.append(current_entry)

    records = []
    for e in all_entries:
        if not e['amounts']:
            continue
            
        credit = None
        debit = None
        balance = None
        
        valid_amounts = e['amounts']
        clean_nums = [_amount_to_number(a) for a in valid_amounts]
        
        # In BOP statements with 3 columns [Dr, Cr, Balance]
        if len(clean_nums) >= 3:
            debit = clean_nums[0]
            credit = clean_nums[1]
            balance = clean_nums[2]
        elif len(clean_nums) == 2:
            tx_amt = clean_nums[0]
            balance = clean_nums[1]
            desc_lower = e['desc'].lower()
            if any(kw in desc_lower for kw in ['credit', 'encashment', 'deposit', 'received', 'refund', 'rev', 'rtgs']):
                credit = tx_amt
            else:
                debit = tx_amt
        elif len(clean_nums) == 1:
            balance = clean_nums[0]
            
        records.append({
            'date': e['date'],
            'desc': e['desc'],
            'credit': credit,
            'debit': debit,
            'balance': balance
        })

    df = pd.DataFrame(records)
    print(f"File: {pdf_path} -> Total parsed rows: {len(df)}")
    print(df.head(15).to_string())
    print("\nFilled counts:")
    for col in df.columns:
        cnt = df[col].notna().sum()
        print(f"  {col}: {cnt}/{len(df)}")

if __name__ == "__main__":
    parse_bop_statement("C:/Users/ranau/Downloads/m javed statement.pdf")
