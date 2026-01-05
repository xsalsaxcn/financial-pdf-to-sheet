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
KNOWN_UNITS = ["%", "times", "days", "yrs", "Rp"]

# =============================
# HELPERS
# =============================
def clean_number(value: str):
    if not value:
        return None
    value = value.replace(".", "").replace(",", ".")
    try:
        return float(value)
    except:
        return None


def normalize_line(line: str) -> str:
    line = line.replace("*", "")
    line = re.sub(r"(\d)(-)", r"\1 -", line)  # fix -71days
    return line.strip()


def split_value_unit(token):
    for unit in KNOWN_UNITS:
        if token.endswith(unit):
            num = token.replace(unit, "")
            return clean_number(num), unit
    return clean_number(token), ""


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
        for k, v in KPI_CATEGORIES.items():
            if k in line:
                current_category = v
                break

        if not current_category:
            continue

        # === IMPORTANCE ===
        importance = None
        for lvl in IMPORTANCE_LEVELS:
            if line.endswith(lvl):
                importance = lvl
                break

        if not importance:
            continue

        tokens = line.split()

        try:
            idx = tokens.index(importance)

            # ===== TREND =====
            trend_val, trend_unit = split_value_unit(tokens[idx - 2])
            if tokens[idx - 1] in KNOWN_UNITS:
                trend_unit = tokens[idx - 1]

            # ===== TARGET =====
            target_val, target_unit = split_value_unit(tokens[idx - 4])
            if tokens[idx - 3] in KNOWN_UNITS:
                target_unit = tokens[idx - 3]

            # ===== RESULT =====
            result_val, result_unit = split_value_unit(tokens[idx - 6])
            if tokens[idx - 5] in KNOWN_UNITS:
                result_unit = tokens[idx - 5]

            # ===== KPI NAME =====
            kpi_name = " ".join(tokens[: idx - 6])

            rows.append([
                period,
                current_category,
                kpi_name.strip(),
                result_val,
                result_unit,
                target_val,
                target_unit,
                trend_val,
                trend_unit,
                importance
            ])

        except Exception:
            continue

    return rows
