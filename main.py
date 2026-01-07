# main.py
# Orkestrasi: baca PDF, parse, upload ke Drive, tulis ke Google Sheet

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
SPREADSHEET_NAME = "FINANCIAL_REPORT"


# =========================
# CORE FUNCTION
# (dipanggil dari Streamlit: app.py)
# =========================
def process_pdf(pdf_path: str = "report.pdf"):
    """
    Baca PDF, parse semua section, upload PDF ke Drive,
    lalu update Google Sheet. Return dict ringkasan.
    """

    print("📄 Reading PDF...")
    text = extract_text(pdf_path)

    print("🗓️ Detecting period...")
    period = detect_period(text)
    print(f"Period: {period}")

    # ---------- PARSING ----------
    print("📊 Parsing P&L...")
    pl_data = parse_profit_loss(text)

    print("🏦 Parsing Balance Sheet...")
    bs_data = parse_balance_sheet(text)

    print("💰 Parsing Cash Flow...")
    cf_data = parse_cashflow(text)

    print("📈 Parsing KPI Result...")
    kpi_rows = parse_kpi_result(text, period)

    # ---------- UPLOAD PDF -> DRIVE ----------
    print("☁️ Uploading PDF to Google Drive...")
    drive_info = upload_pdf_to_drive(pdf_path, period)

    # upload_pdf_to_drive biasanya return dict:
    # { "file_id": ..., "file_name": ..., "link": ... }
    if isinstance(drive_info, dict):
        drive_link = drive_info.get("link")
    else:
        # jaga-jaga kalau fungsinya cuma return string
        drive_link = str(drive_info)

    print("🔗 Connecting to Google Sheet...")
    sheet = connect_sheet(SPREADSHEET_NAME)

    # ---------- WORKSHEETS ----------
    pl_ws = get_or_create_worksheet(sheet, "P&L")
    bs_ws = get_or_create_worksheet(sheet, "Balance Sheet")
    cf_ws = get_or_create_worksheet(sheet, "Cash Flow")
    kpi_ws = get_or_create_worksheet(sheet, "KPI Result")

    # ---------- TULIS FINANCIAL DATA ----------
    print("⬆️ Updating P&L...")
    upsert_financial_data(pl_ws, period, pl_data)

    print("⬆️ Updating Balance Sheet...")
    upsert_financial_data(bs_ws, period, bs_data)

    print("⬆️ Updating Cash Flow...")
    upsert_financial_data(cf_ws, period, cf_data)

    # ---------- KPI (SUDAH HANDLE OVERWRITE DI DALAM append_kpi_rows) ----------
    print("➕ Upserting KPI Result...")
    append_kpi_rows(kpi_ws, kpi_rows)

    # ---------- META SHEET: SIMPAN LINK DRIVE PER PERIOD ----------
    print("🔗 Saving Drive link to META sheet...")
    meta_ws = get_or_create_worksheet(sheet, "META")

    # Pastikan header
    header = meta_ws.row_values(1)
    if not header:
        meta_ws.update("A1:B1", [["Period", "PDF Drive Link"]])
        existing_periods = []
    else:
        existing_periods = meta_ws.col_values(1)

    # Cari apakah period sudah pernah ada di META
    row_to_update = None
    # skip header (row 1)
    for idx, p in enumerate(existing_periods[1:], start=2):
        if p == period:
            row_to_update = idx
            break

    if row_to_update is None:
        # belum ada -> append row baru
        meta_ws.append_row([period, drive_link])
    else:
        # sudah ada -> overwrite baris tersebut
        meta_ws.update(f"A{row_to_update}:B{row_to_update}", [[period, drive_link]])

    print("✅ ALL FINANCIAL DATA SUCCESSFULLY UPDATED")

    return {
        "period": period,
        "pl_rows": len(pl_data),
        "bs_rows": len(bs_data),
        "cf_rows": len(cf_data),
        "kpi_rows": len(kpi_rows),
        "drive_link": drive_link,
    }


# =========================
# CLI SUPPORT (opsional)
# =========================
if __name__ == "__main__":
    # Jalankan manual dari terminal:
    # python main.py
    result = process_pdf("report.pdf")
    print(result)
