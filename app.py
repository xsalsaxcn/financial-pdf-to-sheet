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

st.set_page_config(
    page_title="Financial Report Upload",
    page_icon="🦆",
    layout="wide",
)


# =========================
# GLOBAL CSS (LAYOUT & THEME)
# =========================
def inject_css():
    st.markdown(
        """
        <style>
        /* background halaman */
        .stApp {
            background: radial-gradient(circle at top, #111827 0, #020617 55%, #020617 100%);
        }

        /* container utama */
        .block-container {
            max-width: 1100px;
            padding-top: 2.3rem;
            padding-bottom: 3rem;
        }

        /* "kartu" besar (nav + body) */
        .shell {
            border-radius: 30px;
            overflow: hidden;
            box-shadow:
                0 26px 70px rgba(15,23,42,0.85),
                0 0 0 1px rgba(15,23,42,0.45);
        }

        .shell-nav {
            background: #020617;
            color: #e5e7eb;
            padding: 0.75rem 1.8rem;
            display: flex;
            align-items: baseline;
            gap: 8px;
        }
        .shell-nav-title {
            font-weight: 600;
        }
        .shell-nav-sub {
            font-size: 0.82rem;
            opacity: 0.9;
        }

        .shell-body {
            /* biar nyatu sama background gelap, teks nanti kita buat terang */
            background: transparent;
            padding: 2rem 2.4rem 2.1rem 2.4rem;
        }

        /* hero kiri: teks */
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.75rem;
            padding: 0.25rem 0.9rem;
            border-radius: 999px;
            background: rgba(15,23,42,0.9);
            border: 1px solid rgba(148,163,184,0.5);
            color: #e5e7eb;
            margin-bottom: 0.8rem;
        }
        .hero-badge-dot {
            width: 7px;
            height: 7px;
            border-radius: 999px;
            background: #22c55e;
        }
        .hero-title {
            font-size: 2.15rem;
            font-weight: 800;
            color: #f9fafb;          /* PUTIH, jelas di background gelap */
            margin-bottom: 0.4rem;
        }
        .hero-subtitle {
            font-size: 0.95rem;
            color: #e5e7eb;          /* abu terang */
            max-width: 430px;
            margin-bottom: 1.4rem;
        }

        /* panel upload di kanan (sengaja terang) */
        .upload-panel {
            background: #eff6ff;
            border-radius: 22px;
            border: 2px dashed #60a5fa;
            padding: 1.0rem 1.1rem 1.2rem 1.1rem;
        }
        .upload-panel * {
            color: #1e293b !important;   /* teks di panel tetap gelap & jelas */
        }
        .upload-title {
            font-weight: 600;
            margin-bottom: 0.25rem;
            font-size: 0.96rem;
        }
        .upload-sub {
            font-size: 0.82rem;
            color: #64748b !important;
            margin-bottom: 0.6rem;
        }

        /* banner flow */
        .flow-card {
            margin-top: 1.5rem;
            background: #020617;
            border-radius: 22px;
            padding: 1.0rem 1.3rem 1.3rem 1.3rem;
            box-shadow: 0 18px 55px rgba(15,23,42,0.85);
        }
        .flow-caption {
            font-size: 0.8rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: #9ca3af;
            margin-bottom: 0.4rem;
        }

        /* tips */
        .tips-wrapper {
            margin-top: 1.7rem;
            background: rgba(15,23,42,0.96);
            color: #e5e7eb;
            border-radius: 20px;
            padding: 1rem 1.6rem 1.1rem 1.6rem;
            box-shadow: 0 18px 45px rgba(15,23,42,0.9);
            font-size: 0.9rem;
        }
        .tips-title {
            font-weight: 600;
            margin-bottom: 0.2rem;
        }
        .tips-ul {
            margin: 0.25rem 0 0 0;
            padding-left: 1.1rem;
        }
        .tips-ul li {
            margin-bottom: 0.15rem;
        }

        /* footer */
        .footer {
            margin-top: 1.6rem;
            text-align: center;
            font-size: 0.8rem;
            color: #9ca3af;
        }

        /* kecilkan jarak default antara markdown */
        .element-container:has(> .stMarkdown) {
            margin-bottom: 0.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# CORE PROCESS FUNCTION
# =========================
def process_pdf(pdf_path: str = "report.pdf") -> dict:
    """
    Baca PDF, parse semua section, upload PDF ke Drive,
    update Google Sheet, dan kembalikan ringkasan.
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

    # ===== Upload PDF ke Google Drive (OAuth user) =====
    print("☁️ Uploading PDF to Google Drive...")
    drive_info = upload_pdf_to_drive(pdf_path, period)
    drive_link = None
    if isinstance(drive_info, dict):
        drive_link = drive_info.get("link")
    print("📎 Drive Link:", drive_link)

    # ===== Update Google Sheet =====
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

    print("➕ Updating KPI Result (overwrite same period)...")
    append_kpi_rows(kpi_ws, kpi_rows)

    # Simpan log period + link di sheet META
    meta_ws = get_or_create_worksheet(sheet, "META")
    if not meta_ws.row_values(1):
        meta_ws.append_row(["Period", "PDF Drive Link"])
    if drive_link:
        meta_ws.append_row([period, drive_link])

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
# STREAMLIT LAYOUT
# =========================
def main():
    inject_css()

    # ---------- SHELL (NAV + BODY DALAM 1 KARTU) ----------
    st.markdown('<div class="shell">', unsafe_allow_html=True)

    # NAV BAR
    st.markdown(
        """
        <div class="shell-nav">
            <div class="shell-nav-title">Financial Report Upload</div>
            <div class="shell-nav-sub">• Upload PDF → Auto Parse → Google Sheet & Drive</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # BODY KARTU
    st.markdown('<div class="shell-body">', unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1.2, 1.0, 1.25])

    # ----- LEFT: TITLE & DESKRIPSI -----
    with col_left:
        st.markdown(
            """
            <div class="hero-badge">
                <div class="hero-badge-dot"></div>
                <span>InHarmony Financial Automation</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="hero-title">Automate Your Financial Data Flow</div>
            <div class="hero-subtitle">
                Effortless reporting with a friendly guide. Upload laporan keuangan PDF,
                biarkan bot mengirim angka ke Google Sheet <b>"FINANCIAL_REPORT"</b> dan
                menyimpan PDF-nya di Google Drive.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ----- CENTER: BEBEK -----
    with col_center:
        st.image("assets/duck.png", use_column_width=True)

    # ----- RIGHT: UPLOAD PANEL -----
    uploaded_file = None
    with col_right:
        st.markdown('<div class="upload-panel">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="upload-title">Upload Financial PDF Report</div>
            <div class="upload-sub">Drag & drop atau klik tombol di bawah (max 20MB, PDF).</div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            " ",
            type=["pdf"],
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # close shell-body
    st.markdown("</div>", unsafe_allow_html=True)  # close shell

    # ---------- BANNER FLOW ----------
    st.markdown('<div class="flow-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="flow-caption">HOW IT WORKS</div>',
        unsafe_allow_html=True,
    )
    st.image("assets/flow_banner.png", use_column_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- PROSES FILE ----------
    result = None
    if uploaded_file is not None:
        pdf_path = "report.pdf"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        with st.spinner("Memproses PDF dan meng-update Google Sheet & Drive..."):
            try:
                result = process_pdf(pdf_path)
            except Exception as e:
                st.error("Terjadi error saat memproses PDF / update Google.")
                st.exception(e)
                return

        st.success("Selesai! ✅ Google Sheet & Google Drive sudah di-update.")

    # ---------- TIPS ----------
    st.markdown('<div class="tips-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="tips-title">Tips penggunaan</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <ul class="tips-ul">
            <li>Pastikan format PDF mengikuti template laporan keuangan InHarmony.</li>
            <li>Kalau periodenya sama (misal <b>Nov 2025</b>), data P&amp;L / BS / Cash Flow
                akan diupdate di kolom periode yang sama.</li>
            <li>KPI untuk periode yang sama akan <b>dioverwrite</b>, tidak ditumpuk ulang.</li>
            <li>Simpan link Google Sheet &amp; Google Drive di bookmark untuk akses cepat.</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- RINGKASAN HASIL ----------
    if result is not None:
        st.subheader("Ringkasan hasil")
        st.json(result)

        drive_link = result.get("drive_link")
        if drive_link:
            st.markdown(
                f"**File PDF di Google Drive:** [Buka file]({drive_link})",
                unsafe_allow_html=True,
            )

    # ---------- FOOTER ----------
    st.markdown(
        """
        <div class="footer">
            created by xslsxcn • Published 2026
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
