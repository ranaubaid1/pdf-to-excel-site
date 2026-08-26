import re

def parse_header_metadata(lines_p1):
    account_title = ""
    account_number = ""
    iban = ""
    opening_balance = None
    closing_balance = None

    def _amount_to_number(amt_str):
        if not amt_str or str(amt_str).strip() == "":
            return None
        clean = amt_str.replace('+', '').replace('-', '').replace('PKR', '').replace(',', '').replace(' ', '').strip()
        try:
            val = float(clean)
            return val
        except ValueError:
            return None

    for i, line in enumerate(lines_p1):
        # 1. Multi-column header labels on line i, values on line i+1
        if 'Opening Balance' in line and 'Closing Balance' in line:
            if i + 1 < len(lines_p1):
                val_line = lines_p1[i + 1]
                amts = re.findall(r'[\d,]+\.\d{2}', val_line)
                if len(amts) >= 2:
                    opening_balance = _amount_to_number(amts[0])
                    closing_balance = _amount_to_number(amts[1])
                elif len(amts) == 1:
                    opening_balance = _amount_to_number(amts[0])

        if 'Account Title' in line and 'Account Number' in line:
            if i + 1 < len(lines_p1):
                val_line = lines_p1[i + 1]
                iban_m = re.search(r'(PK\d{2}[A-Z]{4}\d+)', val_line)
                if iban_m:
                    iban = iban_m.group(1)
                    before_iban = val_line[:val_line.find(iban)].strip()
                    acc_num_m = re.search(r'(\d{10,16})', before_iban)
                    if acc_num_m:
                        account_number = acc_num_m.group(1)
                        account_title = before_iban[:before_iban.find(account_number)].strip()
                    else:
                        account_title = before_iban

    return {
        "account_title": account_title,
        "account_number": account_number,
        "iban": iban,
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
    }

if __name__ == "__main__":
    sample_p1 = [
        "Meezan Bank Account Statement",
        "Account Title Account Number IBAN",
        "AMNA KASHIF 0101700010909 PK68MEZN000101700010909",
        "Opening Balance Closing Balance Address",
        "1,844,447.66 496,730.24 HOUSE NO 123 JOHAR TOWN LAHORE",
    ]
    res = parse_header_metadata(sample_p1)
    print("Parsed Metadata:", res)
    assert res["opening_balance"] == 1844447.66
    assert res["closing_balance"] == 496730.24
    assert res["account_title"] == "AMNA KASHIF"
    assert res["account_number"] == "0101700010909"
    assert res["iban"] == "PK68MEZN000101700010909"
    print("ALL METADATA ASSERTS PASSED PERFECTLY!")
