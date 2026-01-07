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

# =========================
# CONFIG
# =========================
SPREADSHEET_NAME = "FINANCIAL_REPORT"


# =========================
# CORE PROCESS FUNCTION
# =========================
def process_pdf(pdf_path: str = "report.pdf"):
    """
    Baca PDF, parse semua section, dan update Google Sheet.
    Return dict ringkasan hasil.
    """

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
# STREAMLIT APP
# =========================
def main():
    st.set_page_config(page_title="Financial PDF → Google Sheet")

    st.title("Financial PDF → Google Sheet")
    st.write(
        "Upload file laporan keuangan dalam bentuk PDF. "
        "Aplikasi akan mem-parsing dan mengirim hasilnya ke Google Sheet "
        f'"{SPREADSHEET_NAME}".'
    )

    uploaded_file = st.file_uploader("Upload PDF laporan", type=["pdf"])

    if uploaded_file is not None:
        # Simpan PDF ke file sementara di server
        pdf_path = "report.pdf"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        with st.spinner("Memproses PDF dan meng-update Google Sheet..."):
            try:
                result = process_pdf(pdf_path)
            except Exception as e:
                st.error("Terjadi error saat memproses PDF / update Google Sheet.")
                st.exception(e)
                return

        st.success("Selesai! ✅ Google Sheet sudah di-update.")
        st.subheader("Ringkasan hasil")
        st.json(result)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    # Untuk Streamlit, ini yang akan dipanggil
    main()

    # Kalau kamu mau mode CLI manual, bisa tambah opsional begini:
    # import sys
    # if len(sys.argv) > 1 and sys.argv[1] == "--cli":
    #     res = process_pdf("report.pdf")
    #     print(res)
