# =========================
# IMPORTS
# =========================
from extract_pdf import extract_text

from parse_pl import detect_period, parse_profit_loss
from parse_bs import parse_balance_sheet
from parse_cashflow import parse_cashflow
from parse_kpi import parse_kpi_result

from upload_to_drive import upload_pdf_to_drive

from google_sheet import (
    connect_sheet,
    get_or_create_worksheet,
    upsert_financial_data,
    append_kpi_rows,
    upsert_metadata
)

# =========================
# CONFIG
# =========================
PDF_PATH = "report.pdf"
SPREADSHEET_NAME = "FINANCIAL_REPORT"

# =========================
# CORE PROCESS (DIPANGGIL STREAMLIT)
# =========================
def process_pdf(pdf_path=PDF_PATH):

    print("📄 Reading PDF...")
    text = extract_text(pdf_path)

    print("🗓️ Detecting period...")
    period = detect_period(text)

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
    # UPLOAD PDF TO DRIVE
    # =====================
    print("☁️ Uploading PDF to Google Drive...")
    drive_info = upload_pdf_to_drive(pdf_path, period)

    # =====================
    # GOOGLE SHEET
    # =====================
    print("🔗 Connecting to Google Sheet...")
    sheet = connect_sheet(SPREADSHEET_NAME)

    pl_ws = get_or_create_worksheet(sheet, "P&L")
    bs_ws = get_or_create_worksheet(sheet, "Balance Sheet")
    cf_ws = get_or_create_worksheet(sheet, "Cash Flow")
    kpi_ws = get_or_create_worksheet(sheet, "KPI Result")
    meta_ws = get_or_create_worksheet(sheet, "FILES")

    # =====================
    # WRITE DATA
    # =====================
    upsert_financial_data(pl_ws, period, pl_data)
    upsert_financial_data(bs_ws, period, bs_data)
    upsert_financial_data(cf_ws, period, cf_data)

    append_kpi_rows(kpi_ws, kpi_rows)

    # =====================
    # SAVE PDF LINK
    # =====================
    upsert_metadata(
        meta_ws,
        period,
        drive_info["file_name"],
        drive_info["link"]
    )

    return {
        "period": period,
        "pl_rows": len(pl_data),
        "bs_rows": len(bs_data),
        "cf_rows": len(cf_data),
        "kpi_rows": len(kpi_rows),
        "pdf_link": drive_info["link"]
    }


# =========================
# CLI ENTRY (OPTIONAL)
# =========================
if __name__ == "__main__":
    result = process_pdf()
    print("DONE:", result)
