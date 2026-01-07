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

IMPORTANCE_LEVELS = ["Critical", "High", "Medium", "Low"]
# unit yang muncul sebagai token terpisah
KNOWN_UNITS = ["%", "times", "days", "yrs"]

# =============================
# HELPERS
# =============================
def clean_number(value: str):
    if not value:
        return None
    # hilangkan separator ribuan ala Indonesia
    value = value.replace(".", "").replace(",", ".")
    try:
        return float(value)
    except Exception:
        return None


def normalize_line(line: str) -> str:
    line = line.replace("*", "")
    # coba rapikan kasus "-71days" jadi "-71 days"
    line = re.sub(r"(\d)(-)", r"\1 -", line)
    return line.strip()


def split_value_unit(token: str):
    """
    Pecah 1 token menjadi (angka, unit) jika nempel.
    Contoh:
      '59,67%' -> (59.67, '%')
      '1,84'   -> (1.84, '')
      'Rp2.722.196.641' -> (2722196641.0, 'Rp')
    """
    if not token:
        return None, ""

    # khusus currency Rp di depan
    if token.startswith("Rp"):
        num = token[2:]
        return clean_number(num), "Rp"

    # unit nempel di belakang: 59,67% / 45days / 1,84times
    for unit in KNOWN_UNITS:
        if token.endswith(unit):
            num = token[: -len(unit)]
            return clean_number(num), unit

    # cuma angka
    return clean_number(token), ""


def extract_value_from_tail(tokens):
    """
    Ambil 1 nilai (value + optional unit) dari ujung kanan list token,
    lalu kembalikan (value, unit, sisa_tokens).
    """
    if not tokens:
        return None, "", tokens

    last = tokens[-1]

    # kasus unit jadi token terpisah: "1,84 times"
    if last in KNOWN_UNITS:
        unit = last
        if len(tokens) >= 2:
            value_token = tokens[-2]
            value, extra_unit = split_value_unit(value_token)
            if extra_unit and not unit:
                unit = extra_unit
            remaining = tokens[:-2]
        else:
            value = None
            remaining = tokens[:-1]
    else:
        # kasus "59,67%" atau "Rp2.7..."
        value, unit = split_value_unit(last)
        remaining = tokens[:-1]

    return value, unit, remaining


# =============================
# MAIN PARSER
# =============================
def parse_kpi_result(text: str, period: str):
    rows = []
    current_category = None

    for raw in text.splitlines():
        line = normalize_line(raw)
        if not line:
            continue

        # === CATEGORY DETECTION ===
        for key, cat in KPI_CATEGORIES.items():
            if key in line:
                current_category = cat
                break

        if not current_category:
            # belum ketemu kategori, skip
            continue

        # === IMPORTANCE (selalu di ujung) ===
        importance = None
        for lvl in IMPORTANCE_LEVELS:
            if line.endswith(lvl):
                importance = lvl
                break

        if not importance:
            continue

        tokens = line.split()

        # pakai posisi terakhir importance (jaga-jaga kalau ada di tengah)
        try:
            idx_imp = max(i for i, t in enumerate(tokens) if t == importance)
        except ValueError:
            continue

        tokens_no_imp = tokens[:idx_imp]

        try:
            # urutan dari kanan: TREND, TARGET, RESULT
            trend_val, trend_unit, tokens_no_imp = extract_value_from_tail(tokens_no_imp)
            target_val, target_unit, tokens_no_imp = extract_value_from_tail(tokens_no_imp)
            result_val, result_unit, tokens_no_imp = extract_value_from_tail(tokens_no_imp)
        except Exception:
            # kalau parsing gagal, skip baris
            continue

        kpi_name = " ".join(tokens_no_imp).strip()
        if not kpi_name:
            continue

        rows.append([
            period,
            current_category,
            kpi_name,
            result_val,
            result_unit,
            target_val,
            target_unit,
            trend_val,
            trend_unit,
            importance,
        ])

    return rows
