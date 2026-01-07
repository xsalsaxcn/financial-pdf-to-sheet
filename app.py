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

    Return dict ringkasan hasil.
    """

    # -------- EXTRACT & PARSE PDF --------
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

    # -------- UPLOAD PDF KE GOOGLE DRIVE --------
    drive_link = None
    try:
        print("☁️ Uploading PDF to Google Drive...")
        drive_meta = upload_pdf_to_drive(pdf_path, period)
        # upload_pdf_to_drive diasumsikan return dict:
        # { "file_id": ..., "file_name": ..., "link": ... }
        drive_link = drive_meta.get("link")
        print("📎 Drive link:", drive_link)
    except Exception as e:
        # Jangan matikan proses kalau upload gagal
        print("⚠️ Gagal upload ke Google Drive:", e)

    # -------- UPDATE GOOGLE SHEET --------
    print("🔗 Connecting to Google Sheet...")
    sheet = connect_sheet(SPREADSHEET_NAME)

    # Worksheets
    pl_ws = get_or_create_worksheet(sheet, "P&L")
    bs_ws = get_or_create_worksheet(sheet, "Balance Sheet")
    cf_ws = get_or_create_worksheet(sheet, "Cash Flow")
    kpi_ws = get_or_create_worksheet(sheet, "KPI Result")

    print("⬆️ Updating P&L...")
    upsert_financial_data(pl_ws, period, pl_data)

    print("⬆️ Updating Balance Sheet...")
    upsert_financial_data(bs_ws, period, bs_data)

    print("⬆️ Updating Cash Flow...")
    upsert_financial_data(cf_ws, period, cf_data)

    print("➕ Updating KPI Result (overwrite per period)...")
    append_kpi_rows(kpi_ws, kpi_rows)

    print("✅ FINANCIAL DATA UPDATED")

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

    # ---------- GLOBAL CSS ----------
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }
        .upload-card {
            background: #ffffff;
            border-radius: 18px;
            padding: 24px 28px 28px 28px;
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
            border: 1px solid rgba(226, 232, 240, 0.9);
        }
        .tips-card {
            background: #f8fafc;
            border-radius: 18px;
            padding: 20px 24px 24px 24px;
            border: 1px solid rgba(226, 232, 240, 0.9);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---------- HERO BANNER ----------
    with st.container():
        try:
            # Pastikan file ini ada di: assets/hero_banner.png
            st.image("assets/hero_banner.png", use_column_width=True)
        except Exception:
            # Fallback kalau banner belum ada
            st.title("Financial PDF → Google Sheet")
            st.write(
                "Upload file laporan keuangan dalam bentuk PDF. "
                'Bot akan mem-parsing, mengirim hasilnya ke Google Sheet '
                f'"{SPREADSHEET_NAME}", dan menyimpan PDF ke Google Drive.'
            )

    st.markdown("")  # sedikit jarak di bawah banner

    # ---------- MAIN CONTENT ----------
    col_upload, col_info = st.columns([1.5, 1])

    # ====== KIRI: UPLOAD CARD ======
    with col_upload:
        st.markdown('<div class="upload-card">', unsafe_allow_html=True)

        st.subheader("Upload PDF laporan")
        st.caption(
            "Drag & drop file di sini atau klik **Browse files** "
            "(max 20MB, format PDF)."
        )

        # Hilangkan label default uploader (kita pakai teks sendiri)
        uploaded_file = st.file_uploader(
            "Pilih file PDF",
            type=["pdf"],
            label_visibility="collapsed",
        )

        result = None

        if uploaded_file is not None:
            pdf_path = "report.pdf"
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.read())

            with st.spinner(
                "Memproses PDF, meng-update Google Sheet, dan upload ke Google Drive..."
            ):
                try:
                    result = process_pdf(pdf_path)
                except Exception as e:
                    st.error(
                        "Terjadi error saat memproses PDF / update Google."
                    )
                    st.exception(e)

            if result:
                st.success("Selesai! ✅ Google Sheet & Google Drive sudah di-update.")
                st.subheader("Ringkasan hasil")
                st.json(result)

                if result.get("drive_link"):
                    st.markdown(
                        f'📁 **File PDF di Google Drive:** '
                        f'[Buka file]({result["drive_link"]})'
                    )

        st.markdown("</div>", unsafe_allow_html=True)

    # ====== KANAN: TIPS CARD ======
    with col_info:
        st.markdown('<div class="tips-card">', unsafe_allow_html=True)
        st.subheader("Tips")

        st.markdown(
            """
            - Pastikan format PDF mengikuti template laporan keuangan InHarmony.
            - Kalau periodenya sama (misal **Nov 2025**),  
              data **P&L / Balance Sheet / Cash Flow** akan diupdate di kolom periode yang sama.
            - KPI untuk periode yang sama akan **dioverwrite**, tidak ditumpuk ulang.
            - Simpan link Google Sheet & Google Drive di bookmark untuk akses cepat.
            """
        )

        st.markdown("</div>", unsafe_allow_html=True)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main()
