import json
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1

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

    Pastikan di secrets.toml / Secrets Streamlit kamu ada:

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
def get_or_create_worksheet(sheet, title: str, rows: int = 1000, cols: int = 30):
    """
    Get worksheet if exists, otherwise create it.

    sheet : object spreadsheet dari gspread
    title : nama worksheet (tab) yang dicari / dibuat
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
# =========================
def upsert_financial_data(ws, period: str, data: dict):
    """
    ws      : worksheet object
    period  : misal "Nov 2025"
    data    : dict {Account: value}

    Logic:
    - Baris 1: header → kolom A = "Account", kolom berikutnya = periode
    - Kolom A: daftar account (akun)
    - Kalau account sudah ada → update value di periode tsb
    - Kalau account belum ada → tambah baris baru
    """

    # ===== ENSURE HEADER =====
    headers = ws.row_values(1)
    if not headers:
        ws.update("A1", [["Account"]])
        headers = ["Account"]

    # ===== PERIOD COLUMN =====
    if period in headers:
        col = headers.index(period) + 1  # index dimulai 0, kolom dimulai 1
    else:
        col = len(headers) + 1
        ws.update_cell(1, col, period)

    # ===== EXISTING ACCOUNTS =====
    account_column = ws.col_values(1)  # kolom A

    batch_updates = []

    for account, value in data.items():
        # Cari baris untuk account ini
        if account in account_column:
            row = account_column.index(account) + 1
        else:
            # Account baru → tambah di baris paling bawah
            row = len(account_column) + 1
            account_column.append(account)

            batch_updates.append(
                {
                    "range": f"A{row}",
                    "values": [[account]],
                }
            )

        # Sel untuk periode + account ini
        cell = rowcol_to_a1(row, col)
        batch_updates.append(
            {
                "range": cell,
                "values": [[value]],
            }
        )

    if batch_updates:
        ws.batch_update(batch_updates, value_input_option="USER_ENTERED")


# =========================
# APPEND KPI RESULT
# =========================
def append_kpi_rows(ws, rows: list):
    """
    ws   : worksheet object
    rows : list of rows, format:
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

    Fungsi ini hanya append (tambah baris di bawah).
    """

    if not rows:
        return

    # ===== ENSURE HEADER =====
    if not ws.row_values(1):
        ws.append_row(
            [
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
        )

    ws.append_rows(rows, value_input_option="USER_ENTERED")
