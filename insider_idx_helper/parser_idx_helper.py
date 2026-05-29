from collections import defaultdict

from insider_idx_helper.utils.helper import (
    classify_transaction_type, 
    clean_number, 
    clean_percentage,
    standardize_date,
    clean_company_name,
    to_kebab, 
    pop_purpose
)

import fitz
import re
import logging 
import json 


LOGGER = logging.getLogger(__name__)
    

def extract_holder_name(text: str) -> str:
    try: 
        holder_name_pattern = r"Nama \(sesuai SID\)\s*:\s*(.+?)(?:\n|$)"

        holder_name = re.search(holder_name_pattern, text, re.IGNORECASE)
        holder_name = holder_name.group(1) if holder_name else None 
        
        if holder_name:
            holder_name = holder_name.title()
            # Convert any form of "pt" to "PT"
            holder_name = re.sub(r'\bPt\b', 'PT', holder_name)

        return holder_name
    
    except Exception as error: 
        LOGGER.error(f'extract holder name error: {error}')
        return None 


def extract_symbol_and_company_name(text: str) -> dict[str, str]:
    try: 
        # Company Name (with or without line breaks)
        pattern1 = r"Nama Perusahaan Tbk\s*:\s*([A-Z]+)\s*-\s*(.+?)(?=Tbk|PT|Jumlah Saham)"
        
        match = re.search(pattern1, text, re.DOTALL)
        
        if match:
            symbol = match.group(1).strip()
            company_name = match.group(2).strip()
            
            # Clean up company name: remove extra whitespace, newlines, and trailing commas
            company_name = re.sub(r'\s+', ' ', company_name) 
            company_name = company_name.rstrip(',').strip()   
            
            if 'Tbk' in text[match.end():match.end()+20]:
                company_name += ' Tbk'
            
            # LOGGER.info(f'Extracted symbol: {symbol}, company_name: {company_name}')
            symbol = f'{symbol}.JK'
            company_name = company_name

            # print(symbol, company_name)

            return symbol, company_name
        
        return None, None 

    except Exception as error: 
        LOGGER.error(f'extract symbol and company name error: {error}')
        return None, None 


def extract_shares(text: str) -> dict[str, any]: 
    try:
        # Regex Patterns
        shares_before = r"Jumlah Saham Sebelum Transaksi\s*:\s*([\d\.,]+)"
        shares_after = r"Jumlah Saham Setelah Transaksi\s*:\s*([\d\.,]+)"
        
        # New Patterns for Voting Rights (handles optional % sign)
        vote_before = r"Hak Suara Sebelum Transaksi\s*:\s*([\d,]+)\s*%?"
        vote_after = r"Hak Suara Setelah Transaksi\s*:\s*([\d,]+)\s*%?"

        # Search
        shares_before = re.search(shares_before, text, re.IGNORECASE)
        shares_after = re.search(shares_after, text, re.IGNORECASE)
        vote_before = re.search(vote_before, text, re.IGNORECASE)
        vote_after = re.search(vote_after, text, re.IGNORECASE)

        shares_payload = {
            "holding_before": clean_number(shares_before.group(1)) if shares_before else None,
            "holding_after": clean_number(shares_after.group(1)) if shares_after else None,
            "share_percentage_before": clean_percentage(vote_before.group(1)) if vote_before else None,
            "share_percentage_after": clean_percentage(vote_after.group(1)) if vote_after else None
        }

        return shares_payload
    
    except Exception as error:
        LOGGER.error(f'extract shares error: {error}')
        return {} 


def extract_price_transaction(text: str) -> list[dict] | None:
    try:
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # HEADER DETECTION
        header_start_idx = None
        for index, line in enumerate(lines):
            if line == "Jenis" and index + 1 < len(lines) and lines[index + 1] == "Transaksi":
                header_start_idx = index
                break

        if header_start_idx is None:
            return None

        # FIND DATA START
        data_start_idx = None
        for index in range(header_start_idx, len(lines) - 1):
            if lines[index] == "Tujuan" and lines[index + 1] == "Transaksi":
                data_start_idx = index + 2
                break

        if data_start_idx is None:
            transaction_keywords = ["Penjualan", "Pembelian", "Lainnya", "Koreksi", "Pelaksanaan", "(exercise)"]
            for index in range(header_start_idx, len(lines)):
                if lines[index] in transaction_keywords:
                    if lines[index] == "Pelaksanaan" and index + 1 < len(lines) and lines[index + 1] in ["Jumlah", "Saham"]:
                        continue
                    data_start_idx = index
                    break

        if data_start_idx is None:
            return None

        transactions = []
        index = data_start_idx

        transaction_keywords = [
            "Penjualan", "Pembelian", "Lainnya",
            "Koreksi", "Pelaksanaan", "(exercise)", 'Hibah'
        ]
        footer_keywords = [
            "Pemberi", "Keterangan", "Jika",
            "Nama pemegang", "Informasi", "Saya bertanggung", "Hak Suara"
        ]

        # NEW: carries day fragment stripped from previous tx's purpose on page split
        pending_page_split_day = None

        while index < len(lines):
            line = lines[index]

            if any(line.startswith(keyword) for keyword in footer_keywords):
                break

            if line == "Jenis" and index + 1 < len(lines) and lines[index + 1] == "Transaksi":
                while index < len(lines):
                    if lines[index] == "Tujuan" and index + 1 < len(lines) and lines[index + 1] == "Transaksi":
                        index += 2
                        break
                    index += 1
                continue

            if line in transaction_keywords:
                is_real_start = False
                for lookahead in range(1, 10):
                    if index + lookahead >= len(lines):
                        break
                    candidate = lines[index + lookahead]
                    if candidate in ["Tidak", "Ya", "Langsung"]:
                        is_real_start = True
                        break
                    if any(candidate.startswith(keyword) for keyword in footer_keywords):
                        break

                if not is_real_start:
                    index += 1
                    continue

                # PARSE TRANSACTION TYPE
                type_parts = [line]
                index += 1
                while index < len(lines):
                    curr = lines[index]
                    if curr in ["Tidak", "Ya"]:
                        break
                    if curr == "Jenis" or any(curr.startswith(keyword) for keyword in footer_keywords):
                        break
                    type_parts.append(curr)
                    index += 1

                transaction_type = ' '.join(type_parts)

                if index < len(lines) and lines[index] in ["Tidak", "Ya"]:
                    index += 1
                if index < len(lines) and lines[index] == "Langsung":
                    index += 1

                # FIND AMOUNT
                scan_limit = min(index + 100, len(lines))
                saham_found = False

                for scan_idx in range(index, scan_limit):
                    if lines[scan_idx] == "Saham" and scan_idx > 0:
                        prev_line = lines[scan_idx - 1]
                        if ',' in prev_line and any(char.isdigit() for char in prev_line):
                            index = scan_idx - 1
                            saham_found = True
                            break

                # NEW: page-split recovery instead of silent skip
                if not saham_found:
                    if pending_page_split_day is None:
                        index += 1
                        continue

                    amount = None
                    for scan_idx in range(index, min(index + 20, len(lines))):
                        candidate = lines[scan_idx]
                        if ',' in candidate and any(char.isdigit() for char in candidate):
                            amount = candidate
                            index = scan_idx + 1
                            break

                    if amount is None:
                        pending_page_split_day = None
                        index += 1
                        continue

                    price = None
                    for scan_idx in range(index, min(index + 10, len(lines))):
                        candidate = lines[scan_idx]
                        if ',' in candidate and any(char.isdigit() for char in candidate):
                            price = candidate
                            index = scan_idx + 1
                            break

                    # Collect month and year tokens
                    # skipping page header and classification labels
                    date_parts = [pending_page_split_day]
                    purpose_parts = []

                    while index < len(lines):
                        curr = lines[index]

                        if any(curr.startswith(keyword) for keyword in footer_keywords):
                            break

                        if curr == "Jenis" and index + 1 < len(lines) and lines[index + 1] == "Transaksi":
                            while index < len(lines):
                                if lines[index] == "Tujuan" and index + 1 < len(lines) and lines[index + 1] == "Transaksi":
                                    index += 2
                                    break
                                index += 1
                            continue

                        if re.match(r'^(Jan|Feb|Mar|Apr|Mei|Jun|Jul|Ags|Sep|Okt|Nov|Des)', curr, re.IGNORECASE) and len(date_parts) < 3:
                            date_parts.append(curr)
                            index += 1
                            continue

                        if curr.isdigit() and len(curr) == 4 and len(date_parts) < 3:
                            date_parts.append(curr)
                            index += 1
                            continue

                        purpose_parts.append(curr)
                        index += 1

                    date = ' '.join(date_parts)
                    purpose = ' '.join(purpose_parts) if purpose_parts else None
                    pending_page_split_day = None

                    transactions.append({
                        "type": classify_transaction_type(transaction_type, purpose or ''),
                        "amount_transacted": clean_number(amount),
                        "price": clean_number(price),
                        "date": standardize_date(date),
                        "purpose": purpose
                    })
                    continue

                # NORMAL PATH
                amount = lines[index] if index < len(lines) else None
                index += 1

                if index < len(lines) and lines[index] == "Saham":
                    index += 1

                # FIND PRICE
                price = None
                for scan_idx in range(index, min(index + 10, len(lines))):
                    curr = lines[scan_idx]
                    if ',' in curr and any(char.isdigit() for char in curr):
                        price = curr
                        index = scan_idx + 1
                        break

                if price is None:
                    price = lines[index] if index < len(lines) else None
                    index += 1

                # FIND DATE
                date_parts = []
                while index < len(lines):
                    part = lines[index]
                    if re.match(r'^\d{1,2}[\s-]', part):
                        date_parts.append(part)
                        index += 1
                        while index < len(lines):
                            part = lines[index]
                            date_parts.append(part)
                            index += 1
                            if part.isdigit() and len(part) == 4:
                                break
                            if len(date_parts) >= 5:
                                break
                        break
                    index += 1

                date = ' '.join(date_parts) if date_parts else None

                # FIND PURPOSE + detect page-split artifact
                purpose_parts = []
                while index < len(lines):
                    curr = lines[index]

                    if any(curr.startswith(keyword) for keyword in footer_keywords):
                        break
                    if curr == "Jenis" and index + 1 < len(lines) and lines[index + 1] == "Transaksi":
                        break

                    if index + 1 < len(lines) and lines[index + 1] in transaction_keywords:
                        is_next_real_start = False
                        for lookahead in range(2, 12):
                            if index + lookahead >= len(lines):
                                break
                            candidate = lines[index + lookahead]
                            if candidate in ["Tidak", "Ya", "Langsung"]:
                                is_next_real_start = True
                                break
                            if any(candidate.startswith(keyword) for keyword in footer_keywords):
                                break

                        if is_next_real_start:
                            purpose_parts.append(curr)
                            index += 1
                            break

                    purpose_parts.append(curr)
                    index += 1

                raw_purpose = ' '.join(purpose_parts)

                # NEW: detect "INVESTASI Saham 29-" artifact and carry day forward
                artifact_match = re.search(r'\s+Saham\s+(\d{1,2}-)\s*$', raw_purpose)
                if artifact_match:
                    pending_page_split_day = artifact_match.group(1)
                    purpose = raw_purpose[:artifact_match.start()].strip()
                else:
                    pending_page_split_day = None
                    purpose = raw_purpose

                transactions.append({
                    "type": classify_transaction_type(transaction_type, purpose),
                    "amount_transacted": clean_number(amount),
                    "price": clean_number(price),
                    "date": standardize_date(date),
                    "purpose": purpose
                })

            else:
                index += 1

        if not transactions:
            return None

        return transactions

    except Exception as error:
        LOGGER.error(f'extract price transaction error: {error}')
        return None
    

def build_lookup_price_transaction(transactions: list[dict[str, any]]):
    try: 
        transaction_lookup = defaultdict(list)

        for transaction in transactions:
            transaction_type = transaction.get('type')
            transaction_lookup[transaction_type].append(transaction)

        return transaction_lookup

    except Exception as error:
        LOGGER.error(f'Error split_price_transaction: {error}')
        return {}


def compute_transactions(price_transactions: list[dict[str, any]]) -> dict[str, any]:
    if not price_transactions:
        return {}
    
    total_buy_shares = 0
    total_buy_value = 0.0
    
    total_sell_shares = 0
    total_sell_value = 0.0

    total_others_shares = 0
    total_others_value = 0.0

    try:
        has_buy_sell = False 

        for price_transaction in price_transactions: 
            amount = int(price_transaction.get('amount_transacted') or 0)
            price = float(price_transaction.get('price') or 0.0)
            value = amount * price
            
            transaction_type = str(price_transaction.get('type')).lower()

            if transaction_type == 'buy': 
                total_buy_shares += amount
                total_buy_value += value
                has_buy_sell = True 
                
            elif transaction_type == 'sell':
                total_sell_shares += amount
                total_sell_value += value
                has_buy_sell = True 

            else:
                total_others_shares += amount
                total_others_value += value

        if has_buy_sell:
            net_value = total_buy_value - total_sell_value
            net_shares = total_buy_shares - total_sell_shares

            if net_shares > 0:
                calculated_type = 'buy'

            elif net_shares < 0:
                calculated_type = 'sell'

            else:
                calculated_type = 'others'

            if net_shares != 0:
                weighted_average_price = abs(net_value / net_shares)

            else:
                weighted_average_price = 0.0

            return {
                "price": round(weighted_average_price, 3),
                "transaction_value": abs(int(net_value)),
                "transaction_type": calculated_type,
                "net_shares_transacted": net_shares 
            }
        
        else:
            if total_others_shares > 0:
                weighted_average_price = total_others_value / total_others_shares

            else:
                weighted_average_price = 0.0
            
            return {
                "price": round(weighted_average_price, 3),
                "transaction_value": abs(int(total_others_value)),
                "transaction_type": "others",
                "net_shares_transacted": total_others_shares
            }

    except Exception as error:
        LOGGER.error(f"Compute transaction error: {error}")
        return {}


def enrich_transaction(extracted_data: dict[str, any], filing_type: str = 'split'):
    try:
        # Compute top level transaction type, transaction value, price
        price_transaction = extracted_data.get('price_transaction', [])
        transaction_computed = compute_transactions(price_transaction)

        extracted_data['price'] = transaction_computed.get('price')
        extracted_data['transaction_value'] = transaction_computed.get('transaction_value')
        extracted_data['transaction_type'] = transaction_computed.get('transaction_type')
        extracted_data['net_shares_transacted'] = transaction_computed.get('net_shares_transacted')

        # Calculate amount transaction
        if filing_type == 'split': 
            extracted_data['amount_transaction'] = sum(
                transaction.get('amount_transacted', 0)
                for transaction in price_transaction
            ) 

        elif filing_type == 'combine':
            holding_before = extracted_data.get('holding_before', 0)
            holding_after = extracted_data.get('holding_after', 0)
            
            extracted_data['amount_transaction'] = abs(holding_before - holding_after)
    
    except Exception as error:
        LOGGER.error(f'Error run_compute_transaction: {error}')
        return {}
    

def detect_transaction_tables(doc) -> dict:
    keys = ['jenis transaksi', 'klasifikasi saham']
    pages_with_tables = []
    
    for page_num, page in enumerate(doc, start=0):
        text = page.get_text().lower()
        # Normalize all whitespace to single spaces
        text = re.sub(r'\s+', ' ', text)
        
        if all(key in text for key in keys):
            pages_with_tables.append(page_num)
    
    return {
        'count': len(pages_with_tables),
        'pages': pages_with_tables
    }


def collect_extract_shares(doc: fitz.Document, pdf_url: str) -> dict | None:
    extracted_data = {}

    for page_index in [0, 1]:
        if page_index >= len(doc):
            break

        text = doc[page_index].get_text()
        shares_data = extract_shares(text)

        for key, value in shares_data.items():
            if value is not None:
                extracted_data[key] = value

        share_before = extracted_data.get('holding_before')
        share_after = extracted_data.get('holding_after')

        if share_before is not None and share_after is not None:
            if share_before == share_after:
                LOGGER.info(f"skipping {pdf_url}: shares unchanged")
                return None

    # LOGGER.info(f"extracted shares: {extracted_data}\n")

    share_percentage_transaction = round(abs(
        (extracted_data.get('share_percentage_after') or 0.0) -
        (extracted_data.get('share_percentage_before') or 0.0)
    ), 3)
    extracted_data['share_percentage_transaction'] = share_percentage_transaction

    return extracted_data


def enrich_payload(
    doc: fitz.Document,
    extracted_data: dict,
    company_lookup: dict,
    pdf_url: str
) -> None:
    text = doc[0].get_text()

    holder_name = extract_holder_name(text)
    symbol, company_name = extract_symbol_and_company_name(text)

    if company_lookup and symbol:
        company_entry = company_lookup.get(symbol)

        if company_entry:
            company_name = company_entry.get('company_name')

        sector = company_entry.get('sector')
        sub_sector = company_entry.get('sub_sector')

    extracted_data['symbol'] = symbol.upper()
    extracted_data['company_name'] = clean_company_name(company_name)
    extracted_data['holder_name'] = holder_name
    extracted_data['source'] = pdf_url
    extracted_data['sector'] = to_kebab(sector)
    extracted_data['sub_sector'] = to_kebab(sub_sector)


def extract_prices(doc: fitz.Document):
    detected_pages = detect_transaction_tables(doc=doc)
    pages_index = detected_pages.get('pages')

    full_text_lines = [
        doc[page_index].get_text()
        for page_index in range(pages_index[0], pages_index[-1] + 1)
    ]
    combined_text = "\n".join(full_text_lines)

    price_transactions =  extract_price_transaction(combined_text)

    return price_transactions


def parse_document(
    doc: fitz.Document,
    pdf_url: str,
    company_lookup: dict,
) -> list[dict]:
    extracted_data = collect_extract_shares(doc, pdf_url)

    if extracted_data is None:
        return []

    enrich_payload(
        doc, 
        extracted_data, 
        company_lookup,
        pdf_url
    )

    price_transactions = extract_prices(doc)

    combined_filing = {**extracted_data, 'price_transaction': price_transactions}
    enrich_transaction(combined_filing, 'combine')

    price_data_list = build_lookup_price_transaction(price_transactions)

    results = []
    for _, transactions in price_data_list.items():
        purpose = transactions[0].get('purpose') if transactions else None
        pop_purpose(transactions)

        filing = {**extracted_data, 'price_transaction': transactions, 'purpose': purpose}
        enrich_transaction(filing, 'split')

        results.append(filing)

    return results


def parser_new_document(
    pdf_local_path: str,
    pdf_url: str,
) -> list[dict]:
    doc = fitz.open(pdf_local_path)
    
    companies = 'data/companies.json'

    with open(companies, 'r') as file: 
        company_lookup = json.load(file)
    
    try:
        result = parse_document(
            doc, 
            pdf_url, 
            company_lookup
        )

    finally:
        doc.close()

    return result





