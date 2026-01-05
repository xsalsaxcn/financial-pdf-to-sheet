import re

CF_ACCOUNTS = [
    "Operating Cash Flow",
    "Free Cash Flow",
    "Net Cash Flow",
    "Change in Cash on Hand",
]

def parse_cashflow(text):
    data = {}

    for acc in CF_ACCOUNTS:
        pattern = rf"{acc}\s+Rp([\d\.]+)"
        match = re.search(pattern, text)
        if match:
            data[acc] = int(match.group(1).replace(".", ""))

    return data
