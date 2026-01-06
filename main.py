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
PDF_PATH = "report.pdf"
SPREADSHEET_NAME = "FINANCIAL_REPORT"

# =========================
# MAIN PROCESS FUNCTION
# (BISA DIPANGGIL DARI STREAMLIT)
# =========================
def process_pdf(pdf_path=PDF_PATH):
    print("📄 Reading PDF...")
    text = extract_text(pdf_path)

    print("🗓️ Detecting period...")
    period = detect_period(text)
    print("Period:", period)

    # =====================
    # PARSING
    # =====================
    print("📊 Parsing P&L...")
    pl_data = parse_profit_loss(text)

    print("🏦 Parsing Balance Sheet...")
    bs_data = parse_balance_sheet(text)

    print("💰 Parsing Cash Flow...")
    cf_data = parse_cashflow(text)

    print("📈 Parsing KPI Result...")
    kpi_rows = parse_kpi_result(text, period)

    # =====================
    # GOOGLE SHEET
    # =====================
    print("🔗 Connecting to Google Sheet...")
    sheet = connect_sheet(SPREADSHEET_NAME)

    # ===== WORKSHEETS =====
    pl_ws  = get_or_create_worksheet(sheet, "P&L")
    bs_ws  = get_or_create_worksheet(sheet, "Balance Sheet")
    cf_ws  = get_or_create_worksheet(sheet, "Cash Flow")
    kpi_ws = get_or_create_worksheet(sheet, "KPI Result")

    # =====================
    # WRITE DATA
    # =====================
    print("⬆️ Updating P&L...")
    upsert_financial_data(pl_ws, period, pl_data)

    print("⬆️ Updating Balance Sheet...")
    upsert_financial_data(bs_ws, period, bs_data)

    print("⬆️ Updating Cash Flow...")
    upsert_financial_data(cf_ws, period, cf_data)

    print("➕ Appending KPI Result...")
    append_kpi_rows(kpi_ws, kpi_rows)

    print("✅ ALL FINANCIAL DATA SUCCESSFULLY UPDATED")

    return {
        "period": period,
        "pl_rows": len(pl_data),
        "bs_rows": len(bs_data),
        "cf_rows": len(cf_data),
        "kpi_rows": len(kpi_rows)
    }

# =========================
# ENTRY POINT (CMD MODE)
# =========================
if __name__ == "__main__":
    process_pdf()
