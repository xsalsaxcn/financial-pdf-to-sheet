import re

# =============================
# CONFIG
# =============================
KPI_CATEGORIES = {
    "A PROFITABILITY": "PROFITABILITY",
    "B ACTIVITY": "ACTIVITY",
    "C EFFICIENCY": "EFFICIENCY",
    "D ASSET USAGE": "ASSET USAGE",
    "E LIQUIDITY": "LIQUIDITY",
    "F COVERAGE": "COVERAGE",
    "G GEARING": "GEARING",
    "H CASH FLOW": "CASH FLOW",
}

# =============================
# PERIOD DETECTOR
# =============================
def detect_period(text: str) -> str:
    pattern = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})"
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return f"{match.group(1).title()} {match.group(2)}"

    return "Unknown Period"


# =============================
# HELPERS
# =============================
def clean_number(value: str) -> int:
    """
    Bersihkan angka gaya Indonesia / laporan keuangan:
    - buang 'Rp'
    - buang titik (.) sebagai pemisah ribuan
    - buang koma (,)
    - buang tanda minus di depan (untuk P&L kamu sudah treat absolute)
    """
    value = (
        value.replace("Rp", "")
        .replace(".", "")
        .replace(",", "")
        .replace("-", "")
        .strip()
    )
    try:
        return int(value)
    except Exception:
        return 0


def extract_pl_block(text: str) -> str:
    """
    Ambil hanya blok Profit & Loss dari keseluruhan PDF text.
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


# =============================
# DICT VERSION (untuk sheet kolom per periode)
# =============================
def parse_profit_loss(text: str) -> dict:
    """
    Hasil: dict {Account Name: Amount} – versi lama
    """
    pl_data = {}

    pl_text = extract_pl_block(text)
    lines = pl_text.splitlines()

    for line in lines:
        if not line:
            continue

        # skip header
        if "ACCOUNT" in line.upper() or "VARIANCE" in line.upper():
            continue

        # cari angka pertama di baris
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


# =============================
# ROWS VERSION (untuk “tabel seperti KPI Result”)
# =============================
def parse_profit_loss_rows(text: str, period: str):
    """
    Hasil: list of rows dengan format mirip KPI Result:

        [
            Period,        # "Nov 2025"
            "P&L",         # Category (fixed, biar konsisten)
            Account Name,  # misal "Total Revenue"
            Amount,        # angka (int)
            "Rp"           # Currency
        ]

    Dipakai untuk bikin worksheet P&L yang bentuknya vertikal (per baris),
    mirip layout KPI Result.
    """
    pl_dict = parse_profit_loss(text)
    rows = []

    for account, amount in pl_dict.items():
        rows.append(
            [
                period,
                "P&L",
                account,
                amount,
                "Rp",
            ]
        )

    return rows
