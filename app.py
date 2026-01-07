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

from upload_to_drive import upload_pdf_to_drive


# =========================
# CONFIG
# =========================
SPREADSHEET_NAME = "FINANCIAL_REPORT"


# =========================
# CORE PROCESS FUNCTION
# =========================
def process_pdf(pdf_path: str = "report.pdf"):
    """
    Baca PDF, parse semua section, update Google Sheet,
    dan upload PDF ke Google Drive.
    """

    # --- Extract + detect period ---
    text = extract_text(pdf_path)
    period = detect_period(text)

    # --- Parsing semua bagian laporan ---
    pl_data = parse_profit_loss(text)
    bs_data = parse_balance_sheet(text)
    cf_data = parse_cashflow(text)
    kpi_rows = parse_kpi_result(text, period)

    # --- Google Sheet ---
    sheet = connect_sheet(SPREADSHEET_NAME)

    pl_ws = get_or_create_worksheet(sheet, "P&L")
    bs_ws = get_or_create_worksheet(sheet, "Balance Sheet")
    cf_ws = get_or_create_worksheet(sheet, "Cash Flow")
    kpi_ws = get_or_create_worksheet(sheet, "KPI Result")

    # tulis / update data
    upsert_financial_data(pl_ws, period, pl_data)
    upsert_financial_data(bs_ws, period, bs_data)
    upsert_financial_data(cf_ws, period, cf_data)
    append_kpi_rows(kpi_ws, kpi_rows)

    # --- Upload PDF ke Google Drive (OAuth user) ---
    drive_info = upload_pdf_to_drive(pdf_path, period)
    drive_link = drive_info.get("link") if isinstance(drive_info, dict) else None

    # Ringkasan untuk ditampilkan di UI
    return {
        "period": period,
        "pl_rows": len(pl_data),
        "bs_rows": len(bs_data),
        "cf_rows": len(cf_data),
        "kpi_rows": len(kpi_rows),
        "drive_link": drive_link,
    }


# =========================
# STREAMLIT UI
# =========================
def main():
    st.set_page_config(
        page_title="Financial PDF → Google Sheet",
        page_icon="🦆",
        layout="wide",
    )

    # ------- HERO / HEADER -------
    with st.container():
        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown(
                """
                <h1 style="margin-bottom:0;">Financial PDF → Google Sheet</h1>
                <p style="color:#555;">
                    Upload file laporan keuangan dalam bentuk PDF.<br>
                    Bot akan mem-parsing, mengirim hasilnya ke Google Sheet
                    <b>"FINANCIAL_REPORT"</b>, dan menyimpan PDF ke Google Drive.
                </p>
                """,
                unsafe_allow_html=True,
            )

        with col_right:
            # Bebek kuning asisten 🤖🦆
            try:
                st.image("assets/duck.png", width=210)
            except Exception:
                st.write("🦆 (duck.png belum ketemu di folder assets)")

    st.markdown("---")

    # ------- MAIN CONTENT: Upload Area -------
    col_upload, col_info = st.columns([1.4, 1])

    with col_upload:
        st.subheader("Upload PDF laporan")

        upload_box = st.empty()
        uploaded_file = upload_box.file_uploader(
            "Drag & drop file di sini atau klik **Browse files**",
            type=["pdf"],
        )

        if uploaded_file is not None:
            # Simpan sementara
            pdf_path = "report.pdf"
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.read())

            with st.spinner("Memproses PDF, update Google Sheet & upload ke Drive..."):
                try:
                    result = process_pdf(pdf_path)
                except Exception as e:
                    st.error("Terjadi error saat memproses PDF / update Google.")
                    st.exception(e)
                    return

            st.success("Selesai! ✅ Google Sheet & Google Drive sudah di-update.")

            st.subheader("Ringkasan hasil")
            st.json(result)

            # Link ke Google Drive, kalau tersedia
            if result.get("drive_link"):
                st.markdown(
                    f"📁 **File PDF di Google Drive:** "
                    f"[Buka file]({result['drive_link']})"
                )

    # ------- SIDE INFO / FOOTER -------
    with col_info:
        st.subheader("Tips")
        st.markdown(
            """
            - Pastikan format PDF mengikuti template laporan keuangan InHarmony.
            - Kalau periodenya sama (misal *Nov 2025*),  
              data P&L / BS / Cash Flow akan diupdate di kolom periode yang sama.
            - KPI untuk periode yang sama akan dioverwrite, bukan ditumpuk ulang.
            """
        )

        st.markdown("---")
        st.markdown(
            "<p style='text-align:center;color:#888;'>"
            "created by <b>xlsxscn</b> • Published 2026"
            "</p>",
            unsafe_allow_html=True,
        )


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main()
