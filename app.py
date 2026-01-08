# app.py
import os
import streamlit as st

# pastikan main.py punya fungsi process_pdf(pdf_path) yang sudah berjalan
from main import process_pdf


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Financial Report Upload",
    page_icon="📊",
    layout="wide",
)


# =========================
# CUSTOM CSS
# =========================
st.markdown(
    """
    <style>
    /* GLOBAL BACKGROUND */
    .stApp {
        background: radial-gradient(circle at top, #192845 0%, #040f27 45%, #020815 100%);
        color: #f5f7fb;
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    /* HILANGKAN PADDING DEFAULT ATAS */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }

    /* TOP BREADCRUMB BAR */
    .top-bar {
        background: rgba(2, 8, 21, 0.92);
        padding: 0.4rem 2.5rem;
        font-size: 0.78rem;
        color: #c9d4ff;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.55);
    }
    .top-bar span.path-main {
        font-weight: 600;
        color: #ffffff;
    }
    .top-bar span.path-sep {
        opacity: 0.45;
    }

    /* MAIN WRAPPER (FULL WIDTH, TAPI ADA MARGIN KIRI KANAN) */
    .app-main-container {
        padding: 1.5rem 3rem 0 3rem;
    }

    /* SMALL BADGE */
    .app-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.9rem;
        border-radius: 999px;
        font-size: 0.75rem;
        color: #e8f5ff;
        background: radial-gradient(circle at left, #2dd57b 0%, #0f9b4f 40%, #062b38 100%);
        box-shadow: 0 6px 20px rgba(9, 188, 138, 0.45);
        margin-top: 0.5rem;
        margin-bottom: 0.8rem;
    }
    .app-badge-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #d4ffe7;
        box-shadow: 0 0 12px rgba(226, 255, 241, 0.9);
    }

    /* HERO SECTION */
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: 0.02em;
        color: #fdfdff;
        margin-bottom: 0.25rem;
    }
    .hero-subtitle {
        font-size: 0.96rem;
        max-width: 540px;
        color: #d2ddff;
    }
    .hero-subtitle strong {
        color: #ffffff;
    }

    /* UPLOAD CARD */
    .upload-card {
        background: radial-gradient(circle at top left, #101b3a 0%, #050c1f 55%, #040917 100%);
        border-radius: 18px;
        padding: 1rem 1.4rem 1.2rem 1.4rem;
        box-shadow:
            0 18px 45px rgba(0, 0, 0, 0.85),
            0 0 0 1px rgba(164, 189, 255, 0.12);
        border: 1px solid rgba(116, 153, 255, 0.35);
        position: relative;
        overflow: hidden;
    }
    .upload-card::before {
        content: "";
        position: absolute;
        inset: -60%;
        background:
            radial-gradient(circle at 0% 0%, rgba(128, 187, 255, 0.18) 0%, transparent 60%),
            radial-gradient(circle at 100% 0%, rgba(255, 201, 120, 0.14) 0%, transparent 55%);
        opacity: 0.9;
        pointer-events: none;
    }
    .upload-card-inner {
        position: relative;
        z-index: 1;
    }
    .upload-title {
        font-size: 0.96rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }
    .upload-subtitle {
        font-size: 0.78rem;
        color: #dbe7ff;
        opacity: 0.9;
        margin-bottom: 0.8rem;
    }

    /* UPLOAD AREA */
    .upload-area {
        background: radial-gradient(circle at top left, #111828 0%, #070c1b 55%, #050712 100%);
        border-radius: 18px;
        padding: 0.85rem 1.1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        border: 1px dashed rgba(186, 205, 255, 0.45);
        box-shadow:
            0 18px 40px rgba(2, 6, 23, 0.8),
            inset 0 0 0 0.5px rgba(255, 255, 255, 0.05);
    }
    .upload-area-left {
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    .upload-icon-wrapper {
        width: 40px;
        height: 40px;
        border-radius: 999px;
        background: radial-gradient(circle at 30% 0%, #5cd2ff 0%, #1d8fff 35%, #1143a0 80%);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 12px 30px rgba(0, 132, 255, 0.6);
    }
    .upload-icon-wrapper svg {
        width: 22px;
        height: 22px;
        color: #eaf5ff;
    }
    .upload-area-text-main {
        font-size: 0.85rem;
        color: #f7fbff;
        font-weight: 500;
    }
    .upload-area-text-sub {
        font-size: 0.76rem;
        color: #c2d4ff;
        opacity: 0.9;
    }

    .upload-browse-btn button {
        background: linear-gradient(135deg, #ffc447 0%, #ff9a1f 45%, #ff8a2f 100%);
        color: #2a1600;
        font-weight: 600 !important;
        border-radius: 999px !important;
        border: none;
        padding: 0.4rem 1.4rem;
        box-shadow: 0 10px 25px rgba(255, 170, 60, 0.65);
    }
    .upload-browse-btn button:hover {
        filter: brightness(1.05);
        transform: translateY(-0.5px);
    }

    /* HOW IT WORKS */
    .section-title {
        font-size: 0.84rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #8ea6ff;
        margin-top: 1.8rem;
        margin-bottom: 0.6rem;
    }
    .how-card {
        background: linear-gradient(135deg, rgba(26, 39, 83, 0.96), rgba(10, 20, 46, 0.96));
        border-radius: 24px;
        padding: 1.2rem 1.3rem 1.3rem 1.3rem;
        box-shadow:
            0 22px 55px rgba(0, 0, 0, 0.85),
            0 0 0 1px rgba(145, 176, 255, 0.35);
    }

    /* TIPS */
    .tips-card {
        background: radial-gradient(circle at top left, rgba(21, 32, 62, 0.96), rgba(7, 11, 24, 0.98));
        border-radius: 22px;
        padding: 1.2rem 1.5rem;
        box-shadow:
            0 18px 40px rgba(0, 0, 0, 0.9),
            0 0 0 1px rgba(123, 152, 224, 0.38);
        margin-top: 0.5rem;
    }
    .tips-card h4 {
        font-size: 0.92rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #c6d6ff;
        margin-bottom: 0.7rem;
    }
    .tips-card ul {
        padding-left: 1.1rem;
        margin-bottom: 0;
    }
    .tips-card li {
        font-size: 0.82rem;
        color: #e2ecff;
        margin-bottom: 0.2rem;
    }

    /* FOOTER */
    .footer {
        text-align: center;
        font-size: 0.75rem;
        color: #9fb1ff;
        margin-top: 1.2rem;
        opacity: 0.82;
    }
    .footer span.sig {
        font-weight: 500;
        color: #f1f4ff;
    }

    /* RESULT JSON (HASIL PARSING) */
    .result-json {
        margin-top: 1rem;
        background: rgba(3, 10, 30, 0.96);
        border-radius: 18px;
        padding: 0.75rem 1rem 1rem 1rem;
        box-shadow:
            0 14px 32px rgba(0, 0, 0, 0.85),
            0 0 0 1px rgba(129, 161, 255, 0.28);
    }
    .result-json h3 {
        font-size: 0.92rem;
        color: #dfe5ff;
        margin-bottom: 0.4rem;
    }
    .result-json pre {
        background: transparent !important;
        color: #e8f0ff !important;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# MAIN LAYOUT
# =========================

# Top breadcrumb bar
st.markdown(
    """
    <div class="top-bar">
        <span class="path-main">Financial Report Upload</span>
        <span class="path-sep"> • </span>
        <span>Upload PDF → Auto Parse → Google Sheet & Drive</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="app-main-container">', unsafe_allow_html=True)

# Badge
st.markdown(
    """
    <div class="app-badge">
        <div class="app-badge-dot"></div>
        <span>InHarmony Financial Automation</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# HERO
col_left, col_right = st.columns([1.4, 1.2], gap="large")

with col_left:
    st.markdown(
        """
        <div>
            <div class="hero-title">Automate Your Financial Data Flow</div>
            <div class="hero-subtitle">
                Effortless reporting with a friendly guide. Upload laporan keuangan PDF,
                biarkan bot mengirim angka ke Google Sheet <strong>"FINANCIAL_REPORT"</strong>
                dan menyimpan PDF-nya di Google Drive.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown('<div class="upload-card"><div class="upload-card-inner">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="upload-title">Upload Financial PDF Report</div>
        <div class="upload-subtitle">
            Drag &amp; drop atau klik tombol di bawah (maks 20MB, PDF).
        </div>
        """,
        unsafe_allow_html=True,
    )

    # custom upload area (ikon + teks + browse button)
    up_col_left, up_col_right = st.columns([4, 1.4], gap="small")

    with up_col_left:
        st.markdown(
            """
            <div class="upload-area">
                <div class="upload-area-left">
                    <div class="upload-icon-wrapper">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 3a1 1 0 0 1 .86.49l3.5 5.83a1 1 0 1 1-1.72 1.02L13 7.8V16a1 1 0 1 1-2 0V7.8L9.36 10.34a1 1 0 1 1-1.72-1.02l3.5-5.83A1 1 0 0 1 12 3z"/>
                            <path d="M5 15a1 1 0 0 1 1 1 3 3 0 0 0 3 3h6a3 3 0 0 0 3-3 1 1 0 1 1 2 0 5 5 0 0 1-5 5H9a5 5 0 0 1-5-5 1 1 0 0 1 1-1z"/>
                        </svg>
                    </div>
                    <div>
                        <div class="upload-area-text-main">Drag and drop file here</div>
                        <div class="upload-area-text-sub">Limit 20MB per file · PDF only</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with up_col_right:
        # tombol browse aslinya dari st.file_uploader
        st.markdown('<div class="upload-browse-btn">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload PDF laporan",
            type=["pdf"],
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)


# =========================
# HOW IT WORKS SECTION
# =========================
st.markdown('<div class="section-title">HOW IT WORKS</div>', unsafe_allow_html=True)

from pathlib import Path

how_path = Path("assets/how_it_works.png")
if how_path.exists():
    st.markdown('<div class="how-card">', unsafe_allow_html=True)
    st.image(str(how_path), use_column_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="how-card" style="text-align:center; font-size:0.85rem; color:#dfe6ff;">'
        "Tambahkan ilustrasi alur di <code>assets/how_it_works.png</code> untuk menampilkan gambar di sini."
        "</div>",
        unsafe_allow_html=True,
    )


# =========================
# TIPS SECTION
# =========================
st.markdown('<div class="section-title" style="margin-top:1.8rem;">TIPS PENGGUNAAN</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="tips-card">
        <h4>Guideline singkat</h4>
        <ul>
            <li>Pastikan format PDF mengikuti template laporan keuangan InHarmony.</li>
            <li>Kalau periodenya sama (misal <strong>Nov 2025</strong>), data P&amp;L / BS / Cash Flow akan diupdate di kolom periode yang sama.</li>
            <li>KPI untuk periode yang sama akan <strong>di-overwrite</strong>, tidak ditumpuk ulang.</li>
            <li>Simpan link Google Sheet &amp; Google Drive di bookmark untuk akses cepat.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================
# PROCESS UPLOADED FILE
# =========================
result = None
if uploaded_file is not None:
    pdf_path = "report.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner("Memproses PDF dan meng-update Google Sheet & Google Drive..."):
        try:
            result = process_pdf(pdf_path)
            st.success("Selesai! ✅ Google Sheet & Google Drive sudah di-update.")
        except Exception as e:
            st.error("Terjadi error saat memproses PDF / update Google.")
            st.exception(e)

# tampilkan ringkasan hasil jika ada
if result is not None:
    st.markdown('<div class="result-json"><h3>Ringkasan hasil</h3>', unsafe_allow_html=True)
    st.json(result)
    st.markdown("</div>", unsafe_allow_html=True)

    # kalau ada drive_link, tampilkan CTA
    link = result.get("drive_link")
    if link:
        st.markdown(
            f'<p style="margin-top:0.5rem; font-size:0.82rem;">'
            f'📁 File PDF di Google Drive: <a href="{link}" target="_blank">Buka file</a>'
            f"</p>",
            unsafe_allow_html=True,
        )

# FOOTER
st.markdown(
    """
    <div class="footer">
        created by <span class="sig">xslsxcn</span> · Published 2026
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)
