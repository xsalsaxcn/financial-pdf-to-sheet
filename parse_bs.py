import re

BS_ACCOUNTS = [
    "Cash & Equivalents",
    "Accounts Receivable",
    "Inventory",
    "Other Current Assets",
    "Total Current Assets",
    "Fixed Assets",
    "Investments or Other NCAs",
    "Total Non-Current Assets",
    "Total Assets",
    "Tax Liability",
    "Other Current Liabilities",
    "Total Current Liabilities",
    "Long Term Debt",
    "Total Non-Current Liabilities",
    "Total Liabilities",
    "Retained Earnings",
    "Current Earnings",
    "Other Equity",
    "Total Equity",
    "Total Liabilities & Equity",
]

def parse_balance_sheet(text):
    data = {}

    for acc in BS_ACCOUNTS:
        pattern = rf"{acc}\s+Rp([\d\.]+)"
        match = re.search(pattern, text)
        if match:
            value = int(match.group(1).replace(".", ""))
            data[acc] = value

    return data
