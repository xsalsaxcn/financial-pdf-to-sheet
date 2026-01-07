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
        # diasumsikan return dict: { "file_id": ..., "file_name": ..., "link": ... }
        drive_link = drive_meta.get("link")
        print("📎 Drive link:", drive_link)
    except Exception as e:
        print("⚠️ Gagal upload ke Google Drive:", e)

    # -------- UPDATE GOOGLE SHEET --------
    print("🔗 Connecting to Google Sheet...")
    sheet = connect_sheet(SPREADSHEET_NAME)

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
        page_title="Financial Report Upload",
        page_icon="🦆",
        layout="wide",
    )

    # ---------- GLOBAL STYLE ----------
    st.markdown(
        """
        <style>
        /* background halaman */
        body {
            background: linear-gradient(180deg, #020617 0%, #0b1120 40%, #020617 100%);
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }
        /* hero card utama */
        .hero-card {
            background: #f9fafb;
            border-radius: 28px;
            padding: 32px 40px;
            box-shadow: 0 32px 80px rgba(15, 23, 42, 0.5);
            border: 1px solid rgba(148, 163, 184, 0.35);
        }
        .hero-topbar {
            background: #020617;
            border-radius: 18px 18px 0 0;
            padding: 14px 24px;
            color: #e5e7eb;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 24px;
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: #020617;
            margin-bottom: 0.4rem;
        }
        .hero-subtitle {
            font-size: 0.98rem;
            color: #64748b;
        }
        /* upload panel kanan */
        .upload-panel {
            background: #e0f2fe;
            border-radius: 24px;
            padding: 20px 22px 24px 22px;
            border: 2px dashed #60a5fa;
        }
        .upload-panel h5 {
            margin-bottom: 0.2rem;
        }
        .upload-panel .stFileUploader {
            padding-top: 8px;
        }
        /* hilangkan label uploader default */
        .upload-panel label[data-baseweb="file-uploader"] {
            display: none;
        }
        /* tips card bawah */
        .tips-card {
            background: rgba(15, 23, 42, 0.85);
            border-radius: 18px;
            padding: 18px 22px 20px 22px;
            color: #e5e7eb;
            border: 1px solid rgba(148, 163, 184, 0.5);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---------- HERO CARD ----------
    with st.container():
        st.markdown('<div class="hero-card">', unsafe_allow_html=True)

        # topbar kecil biru tua
        st.markdown(
            """
            <div class="hero-topbar">
              <span style="font-weight:600;">Financial Report Upload</span>
              <span style="margin-left:8px; opacity:0.8;">· Upload PDF → Auto Parse → Google Sheet</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns([1.35, 1])

        # ----- kiri: logo, teks, bebek -----
        with col_left:
            # logo (opsional)
            try:
                st.image("assets/logo_inharmony.png", width=90)
            except Exception:
                pass

            st.markdown('<div class="hero-title">Automate Your Financial Data Flow</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="hero-subtitle">'
                "Effortless reporting with a friendly guide. "
                "Upload laporan keuangan PDF, biarkan bot kirim ke Google Sheet & Google Drive."
                "</div>",
                unsafe_allow_html=True,
            )

            st.markdown("")  # jarak kecil

            # duck mascot
            try:
                st.image("assets/duck.png", width=220)
            except Exception:
                st.write("🦆")  # fallback kalau gambar belum ada

        # ----- kanan: upload panel -----
        with col_right:
            st.markdown('<div class="upload-panel">', unsafe_allow_html=True)

            st.markdown("#### Drag and drop file here")
            st.caption("Limit 20MB per file · PDF")

            uploaded_file = st.file_uploader(
                "Upload PDF laporan",
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
                        st.error("Terjadi error saat memproses PDF / update Google.")
                        st.exception(e)

                if result:
                    st.success("Selesai! ✅ Google Sheet & Google Drive sudah di-update.")
                    st.json(result)

                    if result.get("drive_link"):
                        st.markdown(
                            f'📁 **File PDF di Google Drive:** '
                            f'[Buka file]({result["drive_link"]})'
                        )

            st.markdown("</div>", unsafe_allow_html=True)  # end upload-panel

        st.markdown("</div>", unsafe_allow_html=True)  # end hero-card

    # ---------- TIPS SECTION ----------
    st.markdown("")
    with st.container():
        st.markdown('<div class="tips-card">', unsafe_allow_html=True)
        st.markdown("#### Tips penggunaan")
        st.markdown(
            """
            - Pastikan format PDF mengikuti template laporan keuangan InHarmony.
            - Kalau periodenya sama (misal **Nov 2025**), data **P&L / BS / Cash Flow**
              akan diupdate di kolom periode yang sama.
            - KPI untuk periode yang sama akan **dioverwrite**, tidak ditumpuk ulang.
            - Simpan link Google Sheet & Google Drive di bookmark untuk akses cepat.
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- FOOTER ----------
    st.markdown(
        """
        <div style="text-align:center; color:#9ca3af; font-size:0.8rem; margin-top:2.5rem;">
          created by xslsxcn · Published 2026
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main()
