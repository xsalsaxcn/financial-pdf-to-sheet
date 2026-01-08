import json
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

# =========================
# CONFIG
# =========================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# =========================
# CONNECT TO GOOGLE SHEET
# =========================
def connect_sheet(spreadsheet_name: str):
    """
    Connect to Google Spreadsheet by NAME
    (Streamlit Cloud compatible)

    Di secrets.toml:

    [gcp_service_account]
    json = \"\"\"{ ...JSON service account dari Google... }\"\"\"
    """

    # Ambil JSON mentah dari secrets, lalu parse jadi dict
    info = json.loads(st.secrets["gcp_service_account"]["json"])

    # Buat credentials dari dict JSON
    creds = Credentials.from_service_account_info(
        info,
        scopes=SCOPES,
    )

    # Authorize gspread dengan credentials ini
    client = gspread.authorize(creds)

    # Buka spreadsheet berdasarkan NAMA
    return client.open(spreadsheet_name)


# =========================
# GET OR CREATE WORKSHEET
# =========================
def get_or_create_worksheet(sheet, title: str, rows: int = 1000, cols: int = 10):
    """
    Get worksheet if exists, otherwise create it.
    """
    try:
        return sheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        return sheet.add_worksheet(
            title=title,
            rows=rows,
            cols=cols,
        )


# =========================
# UPSERT FINANCIAL DATA
# (P&L, Balance Sheet, Cash Flow)
# FORMAT: long seperti KPI
# Period | Account | Value
# =========================
def upsert_financial_data(ws, period: str, data: dict):
    """
    ws      : worksheet object
    period  : "Nov 2025"
    data    : dict {Account: value}

    Format sheet:
    A: Period
    B: Account
    C: Value

    - Kalau sheet kosong: tulis header + semua baris
    - Kalau sudah ada data: hapus semua baris untuk period tsb, lalu tulis ulang
      (overwrite, bukan menumpuk)
    """

    # ===== ENSURE HEADER =====
    header = ws.row_values(1)
    if not header:
        header = ["Period", "Account", "Value"]
        ws.update("A1", [header])
    else:
        # kalau header lama bukan 3 kolom, paksa jadi format baru
        if header[:3] != ["Period", "Account", "Value"]:
            header = ["Period", "Account", "Value"]
            ws.update("A1", [header])

    # ===== EXISTING DATA =====
    all_values = ws.get_all_values()  # termasuk header
    existing_rows = all_values[1:] if len(all_values) > 1 else []

    # Filter: simpan hanya baris yang period-nya BUKAN period sekarang
    keep_rows = [r for r in existing_rows if r and r[0] != period]

    # ===== NEW ROWS UNTUK PERIOD INI =====
    new_rows = []
    for account, value in data.items():
        # convert ke string supaya tampil rapi, tapi tetap bisa di-format number di Sheet
        new_rows.append([period, account, value])

    # Gabungkan: baris lama (periode lain) + baris baru (periode ini)
    final_rows = keep_rows + new_rows

    # ===== TULIS ULANG KE SHEET (MINIM REQUEST) =====
    # 1) clear semua kecuali header
    ws.resize(rows=1)  # sisakan baris header saja

    # 2) append semua data sekaligus
    if final_rows:
        ws.append_rows(final_rows, value_input_option="USER_ENTERED")


# =========================
# KPI RESULT (LONG FORMAT)
# =========================
def append_kpi_rows(ws, rows: list):
    """
    rows format (setiap elemen list adalah 1 baris):
    [
        Period,
        Category,
        KPI Name,
        Result,
        Result Unit,
        Target,
        Target Unit,
        Trend,
        Trend Unit,
        Importance
    ]

    Behaviour:
    - Header fixed
    - Semua baris untuk period yang sama akan di-overwrite
      (hapus dulu period tsb, lalu tulis ulang)
    """

    if not rows:
        return

    target_period = rows[0][0]

    # ===== ENSURE HEADER =====
    header = ws.row_values(1)
    if not header:
        header = [
            "Period",
            "Category",
            "KPI Name",
            "Result",
            "Result Unit",
            "Target",
            "Target Unit",
            "Trend",
            "Trend Unit",
            "Importance",
        ]
        ws.update("A1", [header])
    else:
        # Kalau header tidak sesuai, paksa jadi header baru
        expected = [
            "Period",
            "Category",
            "KPI Name",
            "Result",
            "Result Unit",
            "Target",
            "Target Unit",
            "Trend",
            "Trend Unit",
            "Importance",
        ]
        if header[: len(expected)] != expected:
            ws.update("A1", [expected])

    # ===== EXISTING DATA =====
    all_values = ws.get_all_values()
    existing_rows = all_values[1:] if len(all_values) > 1 else []

    # Simpan hanya baris dengan period ≠ target_period
    keep_rows = [r for r in existing_rows if r and r[0] != target_period]

    # Gabungkan: baris lama (periode lain) + baris baru utk target_period
    final_rows = keep_rows + rows

    # ===== TULIS ULANG KE SHEET =====
    ws.resize(rows=1)  # sisakan header
    if final_rows:
        ws.append_rows(final_rows, value_input_option="USER_ENTERED")
