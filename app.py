# =========================
# IMPORTS
# =========================
from extract_pdf import extract_text

from parse_pl import detect_period, parse_profit_loss
from parse_bs import parse_balance_sheet
from parse_cashflow import parse_cashflow
from parse_kpi import parse_kpi_result

from google_sheet import (
    connect_sheet,
    get_or_create_worksheet,
    upsert_financial_data,
    append_kpi_rows
)

# =========================
# CONFIG
# =========================
SPREADSHEET_NAME = "FINANCIAL_REPORT"

# =========================
# CORE PROCESS FUNCTION
# (DIPANGGIL OLEH STREAMLIT)
# =========================
def process_pdf(pdf_path="report.pdf"):
    print("📄 Reading PDF...")
    text = extract_text(pdf_path)

    print("🗓️ Detecting period...")
    period = detect_period(text)

    print("📊 Parsing P&L...")
    pl_data = parse_profit_loss(text)

    print("🏦 Parsing Balance Sheet...")
    bs_data = parse_balance_sheet(text)

    print("💰 Parsing Cash Flow...")
    cf_data = parse_cashflow(text)

    print("📈 Parsing KPI Result...")
    kpi_rows = parse_kpi_result(text, period)

    print("🔗 Connecting to Google Sheet...")
    sheet = connect_sheet(SPREADSHEET_NAME)

    # =========================
    # WORKSHEETS
    # =========================
    pl_ws = get_or_create_worksheet(sheet, "P&L")
    bs_ws = get_or_create_worksheet(sheet, "Balance Sheet")
    cf_ws = get_or_create_worksheet(sheet, "Cash Flow")
    kpi_ws = get_or_create_worksheet(sheet, "KPI Result")

    # =========================
    # WRITE DATA
    # =========================
    upsert_financial_data(pl_ws, period, pl_data)
    upsert_financial_data(bs_ws, period, bs_data)
    upsert_financial_data(cf_ws, period, cf_data)
    append_kpi_rows(kpi_ws, kpi_rows)

    print("✅ FINANCIAL DATA UPDATED")

    return {
        "period": period,
        "pl_rows": len(pl_data),
        "bs_rows": len(bs_data),
        "cf_rows": len(cf_data),
        "kpi_rows": len(kpi_rows),
    }


# =========================
# CLI SUPPORT (OPTIONAL)
# =========================
if __name__ == "__main__":
    result = process_pdf("report.pdf")
    print(result)
