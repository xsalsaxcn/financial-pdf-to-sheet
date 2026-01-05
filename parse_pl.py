import re


def detect_period(text: str) -> str:
    pattern = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})"
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return f"{match.group(1).title()} {match.group(2)}"

    return "Unknown Period"


def clean_number(value: str) -> int:
    value = (
        value.replace("Rp", "")
        .replace(".", "")
        .replace(",", "")
        .replace("-", "")
        .strip()
    )
    try:
        return int(value)
    except:
        return 0


def extract_pl_block(text: str) -> str:
    """
    Extract ONLY Profit & Loss section
    """
    lines = text.splitlines()
    pl_lines = []
    in_pl = False

    STOP_KEYWORDS = [
        "BALANCE SHEET",
        "STATEMENT OF FINANCIAL POSITION",
        "CASH FLOW",
        "STATEMENT OF CASH FLOW",
        "ASSETS",
    ]

    for line in lines:
        clean = line.strip()
        upper = clean.upper()

        # START
        if "PROFIT & LOSS" in upper:
            in_pl = True
            continue

        # STOP
        if in_pl and any(k in upper for k in STOP_KEYWORDS):
            break

        if in_pl and clean:
            pl_lines.append(clean)

    return "\n".join(pl_lines)


def parse_profit_loss(text: str) -> dict:
    """
    Parse clean Profit & Loss table only
    """
    pl_data = {}

    pl_text = extract_pl_block(text)
    lines = pl_text.splitlines()

    for line in lines:
        if not line:
            continue

        if "ACCOUNT" in line.upper() or "VARIANCE" in line.upper():
            continue

        numbers = re.findall(r"\d{1,3}(?:[.,]\d{3})+", line)
        if not numbers:
            continue

        account = line.split(numbers[0])[0]
        account = account.replace("Rp", "").strip()

        if not account:
            continue

        value = clean_number(numbers[0])
        pl_data[account] = value

    return pl_data
