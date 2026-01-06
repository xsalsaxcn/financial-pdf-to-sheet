import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1


# =========================
# CONFIG
# =========================
CREDENTIALS_FILE = "credentials.json"

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
    """
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client.open(spreadsheet_name)


# =========================
# GET OR CREATE WORKSHEET
# =========================
def get_or_create_worksheet(sheet, title: str, rows=1000, cols=30):
    """
    Get worksheet if exists, otherwise create it
    """
    try:
        return sheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        print(f"🆕 Creating worksheet: {title}")
        return sheet.add_worksheet(
            title=title,
            rows=rows,
            cols=cols
        )


# =========================
# UPSERT FINANCIAL DATA
# (P&L, Balance Sheet, Cash Flow)
# =========================
def upsert_financial_data(ws, period: str, data: dict):
    """
    ws      : worksheet object
    period  : "Nov 2025"
    data    : dict {Account: value}
    """

    # ===== ENSURE HEADER =====
    headers = ws.row_values(1)
    if not headers:
        ws.update("A1", [["Account"]])
        headers = ["Account"]

    # ===== PERIOD COLUMN =====
    if period in headers:
        col = headers.index(period) + 1
    else:
        col = len(headers) + 1
        ws.update_cell(1, col, period)

    # ===== EXISTING ACCOUNTS =====
    account_column = ws.col_values(1)

    batch_updates = []

    for account, value in data.items():
        # ROW
        if account in account_column:
            row = account_column.index(account) + 1
        else:
            row = len(account_column) + 1
            account_column.append(account)

            batch_updates.append({
                "range": f"A{row}",
                "values": [[account]]
            })

        # VALUE
        cell = rowcol_to_a1(row, col)
        batch_updates.append({
            "range": cell,
            "values": [[value]]
        })

    # ===== EXECUTE BATCH =====
    if batch_updates:
        ws.batch_update(
            batch_updates,
            value_input_option="USER_ENTERED"
        )


# =========================
# APPEND KPI RESULT
# =========================
def append_kpi_rows(ws, rows: list):
    """
    rows format (WAJIB):
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
    """

    if not rows:
        print("⚠️ No KPI rows to append")
        return

    # ===== ENSURE HEADER =====
    if not ws.row_values(1):
        ws.append_row([
            "Period",
            "Category",
            "KPI Name",
            "Result",
            "Result Unit",
            "Target",
            "Target Unit",
            "Trend",
            "Trend Unit",
            "Importance"
        ])

    ws.append_rows(
        rows,
        value_input_option="USER_ENTERED"
    )


# =========================
# SAVE PDF METADATA (DRIVE)
# =========================
def upsert_metadata(ws, period: str, filename: str, link: str):
    """
    Save uploaded PDF info to Google Sheet
    """

    # ===== ENSURE HEADER =====
    if not ws.row_values(1):
        ws.append_row([
            "Period",
            "Filename",
            "Google Drive Link"
        ])

    rows = ws.get_all_values()

    for i, row in enumerate(rows[1:], start=2):
        if row and row[0] == period:
            ws.update(f"B{i}:C{i}", [[filename, link]])
            return

    ws.append_row([
        period,
        filename,
        link
    ])
