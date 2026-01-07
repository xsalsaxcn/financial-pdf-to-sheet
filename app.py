# =========================
# IMPORTS
# =========================
import streamlit as st

from extract_pdf import extract_text

from parse_pl import detect_period, parse_profit_loss
from parse_bs import parse_balance_sheet
from parse_cashflow import parse_cashflow
from parse_kpi import parse_kpi_result

from google_sheet import (
    connect_sheet,
    get_or_create_worksheet,
    upsert_financial_data,
    append_kpi_rows,
)

from upload_to_drive import upload_pdf_to_drive  # <--- TAMBAHAN


# =========================
# CONFIG
# =========================
SPREADSHEET_NAME = "FINANCIAL_REPORT"


# =========================
# CORE PROCESS FUNCTION
# =========================
def process_pdf(pdf_path: str = "report.pdf"):
    """
    Baca PDF, parse semua section, upload PDF ke Google Drive,
    dan update Google Sheet (P&L, BS, CF, KPI, META).
    Return dict ringkasan hasil.
    """

    # ====== BACA & PARSE PDF ======
    print("📄 Reading PDF...")
    text = extract_text(pdf_path)

    print("🗓️ Detecting period...")
    period = detect_period(text)
    print("Period:", period)

    print("📊 Parsing P&L...")
    pl_data = parse_profit_loss(text)

    print("🏦 Parsing Balance Sheet...")
    bs_data = parse_balance_sheet(text)

    print("💰 Parsing Cash Flow...")
    cf_data = parse_cashflow(text)

    print("📈 Parsing KPI Result...")
    kpi_rows = parse_kpi_result(text, period)

    # ====== UPLOAD PDF KE GOOGLE DRIVE ======
    print("☁️ Uploading PDF to Google Drive...")
    drive_link = upload_pdf_to_drive(pdf_path, period)
    print("📎 Drive Link:", drive_link)

    # ====== UPDATE GOOGLE SHEET ======
    print("🔗 Connecting to Google Sheet...")
    sheet = connect_sheet(SPREADSHEET_NAME)

    # WORKSHEETS
    pl_ws = get_or_create_worksheet(sheet, "P&L")
    bs_ws = get_or_create_worksheet(sheet, "Balance Sheet")
    cf_ws = get_or_create_worksheet(sheet, "Cash Flow")
    kpi_ws = get_or_create_worksheet(sheet, "KPI Result")
    meta_ws = get_or_create_worksheet(sheet, "META")  # <--- TAMBAHAN

    # WRITE DATA
    print("⬆️ Updating P&L...")
    upsert_financial_data(pl_ws, period, pl_data)

    print("⬆️ Updating Balance Sheet...")
    upsert_financial_data(bs_ws, period, bs_data)

    print("⬆️ Updating Cash Flow...")
    upsert_financial_data(cf_ws, period, cf_data)

    print("➕ Appending KPI Result...")
    append_kpi_rows(kpi_ws, kpi_rows)

    # SIMPAN LINK DRIVE DI SHEET META
    print("🔗 Saving Drive link to META sheet...")
    if not meta_ws.row_values(1):
        meta_ws.append_row(["Period", "PDF Drive Link"])
    meta_ws.append_row([period, drive_link])

    print("✅ FINANCIAL DATA UPDATED + PDF UPLOADED")

    return {
        "period": period,
        "pl_rows": len(pl_data),
        "bs_rows": len(bs_data),
        "cf_rows": len(cf_data),
        "kpi_rows": len(kpi_rows),
        "drive_link": drive_link,  # <--- supaya bisa ditampilkan di UI
    }


# =========================
# STREAMLIT APP
# =========================
def main():
    st.set_page_config(page_title="Financial PDF → Google Sheet")

    st.title("Financial PDF → Google Sheet")
    st.write(
        "Upload file laporan keuangan dalam bentuk PDF. "
        "Aplikasi akan mem-parsing, mengupload PDF ke Google Drive, "
        "dan mengirim hasilnya ke Google Sheet "
        f'"{SPREADSHEET_NAME}".'
    )

    uploaded_file = st.file_uploader("Upload PDF laporan", type=["pdf"])

    if uploaded_file is not None:
        # Simpan PDF ke file sementara di server
        pdf_path = "report.pdf"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        with st.spinner("Memproses PDF dan meng-update Google..."):
            try:
                result = process_pdf(pdf_path)
            except Exception as e:
                st.error("Terjadi error saat memproses PDF / update Google.")
                st.exception(e)
                return

        st.success("Selesai! ✅ Google Sheet & Google Drive sudah di-update.")
        st.subheader("Ringkasan hasil")
        st.json(result)

        # Tampilkan link Drive kalau ada
        if result.get("drive_link"):
            st.markdown(
                f"📎 File PDF di Google Drive: [Buka file]({result['drive_link']})"
            )


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main()
