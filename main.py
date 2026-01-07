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
)


# =========================
# CONFIG
# =========================
DEFAULT_PDF_PATH = "report.pdf"
SPREADSHEET_NAME = "FINANCIAL_REPORT"


# =========================
# CORE PIPELINE FUNCTION
# (bisa dipanggil dari Streamlit / CLI)
# =========================
def run_pipeline(pdf_path: str = DEFAULT_PDF_PATH):
    """
    Jalankan seluruh pipeline:
    - Baca & parse PDF
    - Upload PDF ke Google Drive
    - Update Google Sheet (P&L, BS, CF, KPI)
    - Simpan link PDF di sheet META

    Return: dict ringkasan hasil
    """

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
    # UPLOAD PDF → DRIVE
    # =====================
    print("☁️ Uploading PDF to Google Drive...")
    drive_link = upload_pdf_to_drive(pdf_path, period)
    print("📎 Drive Link:", drive_link)

    # =====================
    # GOOGLE SHEET
    # =====================
    print("🔗 Connecting to Google Sheet...")
    sheet = connect_sheet(SPREADSHEET_NAME)

    # ===== WORKSHEETS =====
    pl_ws = get_or_create_worksheet(sheet, "P&L")
    bs_ws = get_or_create_worksheet(sheet, "Balance Sheet")
    cf_ws = get_or_create_worksheet(sheet, "Cash Flow")
    kpi_ws = get_or_create_worksheet(sheet, "KPI Result")

    # =====================
    # WRITE FINANCIAL DATA
    # =====================
    print("⬆️ Updating P&L...")
    upsert_financial_data(pl_ws, period, pl_data)

    print("⬆️ Updating Balance Sheet...")
    upsert_financial_data(bs_ws, period, bs_data)

    print("⬆️ Updating Cash Flow...")
    upsert_financial_data(cf_ws, period, cf_data)

    # =====================
    # KPI RESULT
    # =====================
    print("➕ Appending KPI Result...")
    append_kpi_rows(kpi_ws, kpi_rows)

    # =====================
    # SAVE DRIVE LINK
    # =====================
    print("🔗 Saving Drive link to Google Sheet...")
    meta_ws = get_or_create_worksheet(sheet, "META")

    if not meta_ws.row_values(1):
        meta_ws.append_row(["Period", "PDF Drive Link"])

    meta_ws.append_row([period, drive_link])

    print("✅ ALL FINANCIAL DATA SUCCESSFULLY UPDATED")

    # Ringkasan hasil buat ditampilkan di UI / log
    return {
        "period": period,
        "pl_rows": len(pl_data),
        "bs_rows": len(bs_data),
        "cf_rows": len(cf_data),
        "kpi_rows": len(kpi_rows),
        "drive_link": drive_link,
    }


# =========================
# ENTRY POINT (CLI)
# =========================
if __name__ == "__main__":
    # Kalau dijalankan dengan:
    #   python main.py
    # dia akan pakai DEFAULT_PDF_PATH ("report.pdf")
    result = run_pipeline(DEFAULT_PDF_PATH)
    print(result)
