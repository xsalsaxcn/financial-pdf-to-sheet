# app.py
import os
import streamlit as st
from main import process_pdf  # pastikan main.py punya fungsi process_pdf(pdf_path)

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Financial Report Upload",
    page_icon="🦆",
    layout="wide",
)

# =========================
# GLOBAL STYLE (UPDATED)
# =========================
st.markdown(
    """
    <style>
    /* Background & font global */
    .stApp {
        background: radial-gradient(circle at top,
                    #2f4268 0%,
                    #101b30 45%,
                    #0b1424 100%);
        color: #f5f7fb;
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    h1, h2, h3, h4, h5, h6,
    .stMarkdown, .stText, .stTooltipContent, label, p, li, span {
        color: #f5f7fb !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* NAV BAR */
    .nav-bar {
        font-size: 0.85rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: #c3d5ff;
        padding: 0.5rem 1.25rem;
        border-radius: 999px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: linear-gradient(90deg,
                    rgba(255, 255, 255, 0.12),
                    rgba(16, 27, 48, 0.8));
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(12px);
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }
    .nav-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: #4ade80;
        box-shadow: 0 0 0 5px rgba(74, 222, 128, 0.2);
        display: inline-block;
    }

    .pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.75rem;
        border-radius: 999px;
        background: rgba(15, 118, 110, 0.3);
        border: 1px solid rgba(34, 197, 187, 0.5);
        color: #e0fffc;
        font-size: 0.75rem;
        margin-top: 0.5rem;
    }
    .pill-dot {
        width: 7px;
        height: 7px;
        border-radius: 999px;
        background: #22c55e;
    }

    /* HERO TEXT */
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1.2;
        color: #ffffff;
        margin-bottom: 0.4rem;
    }
    .hero-sub {
        font-size: 0.98rem;
        color: #dde7ff;
        max-width: 520px;
        line-height: 1.5;
    }

    /* UPLOAD CARD – dibesarkan */
    .upload-card {
        background: linear-gradient(145deg,
                    rgba(15, 23, 42, 0.96),
                    rgba(15, 23, 42, 0.9));
        border-radius: 1.4rem;
        padding: 1.4rem 1.6rem 1.5rem 1.6rem; /* LEBIH BESAR */
        box-shadow:
            0 26px 70px rgba(0, 0, 0, 0.75),
            0 0 0 1px rgba(148, 163, 184, 0.35);
        border: 1px solid rgba(148, 163, 184, 0.7);
    }
    .upload-title {
        font-size: 1.02rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        color: #f9fafb;
    }
    .upload-sub {
        font-size: 0.85rem;
        color: #d1d5db;
        margin-bottom: 0.8rem;
    }

    /* ==== FILE UPLOADER: DIGABUNG JADI SATU BLOK === */

    /* Hapus kotak kedua (blok putih) di luar */
    div[data-testid="stFileUploader"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-top: 0.2rem;
    }

    /* Blok utama klik/drag */
    div[data-testid="stFileUploader"] > div {
        background: radial-gradient(circle at top left,
                    rgba(37, 99, 235, 0.25),
                    rgba(15, 23, 42, 0.98));
        border-radius: 1.1rem;
        border: 1px dashed rgba(148, 163, 184, 0.9);
        padding: 0.9rem 1.1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.9rem;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.95);
    }

    /* Hilangkan label default supaya lebih clean */
    div[data-testid="stFileUploader"] label {
        display: none !important;
    }

    /* Teks di sisi kiri (drag & drop, limit, dll) */
    div[data-testid="stFileUploader"] span {
        color: #e5e7eb !important;
        font-size: 0.87rem !important;
    }

    /* Icon cloud – diperbesar */
    div[data-testid="stFileUploader"] svg {
        width: 42px;
        height: 42px;
        stroke-width: 1.7;
    }

    /* Tombol Browse files – tetap kuning, menempel di blok */
    div[data-testid="stFileUploader"] button {
        border-radius: 999px;
        padding: 0.35rem 1.4rem;
        font-size: 0.9rem;
        font-weight: 600;
        background: linear-gradient(135deg, #facc15, #fb923c);
        color: #111827 !important;
        border: none;
        box-shadow: 0 12px 32px rgba(251, 191, 36, 0.5);
        margin-left: 0.5rem;
    }
    div[data-testid="stFileUploader"] button:hover {
        filter: brightness(1.05);
        box-shadow: 0 16px 38px rgba(251, 191, 36, 0.65);
    }

    /* SECTION DIVIDER */
    .section-divider {
        height: 6px;
        border-radius: 999px;
        background: linear-gradient(90deg,
                    rgba(148, 163, 184, 0.1),
                    rgba(148, 163, 184, 0.4),
                    rgba(148, 163, 184, 0.1));
        margin: 0.4rem 0 1.1rem 0;
    }
    .section-label {
        font-size: 0.78rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #cbd5f5;
        margin-bottom: 0.2rem;
    }

    /* TIPS CARD */
    .tips-card {
        background: radial-gradient(circle at top left,
                    rgba(30, 64, 175, 0.35),
                    rgba(15, 23, 42, 0.98));
        border-radius: 1.2rem;
        padding: 1rem 1.3rem;
        border: 1px solid rgba(148, 163, 184, 0.7);
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.7);
        color: #edf2ff !important;
    }
    .tips-card li {
        color: #e5e9ff !important;
        font-size: 0.9rem;
    }

    .footer-text {
        font-size: 0.72rem;
        color: #cbd5ff;
        opacity: 0.92;
        margin-top: 1.7rem;
        text-align: center;
    }
    .footer-highlight {
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# TOP NAV
# =========================
st.markdown(
    """
    <div class="nav-bar">
        <span class="nav-dot"></span>
        <span>Financial Report Upload</span>
        <span style="opacity:0.65;">· Upload PDF → Auto Parse → Google Sheet & Drive</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="pill-badge">
        <span class="pill-dot"></span>
        <span>InHarmony Financial Automation</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# =========================
# HERO SECTION
# =========================
left, right = st.columns([1.4, 1.2])

with left:
    st.markdown(
        """
        <div class="hero-title">Automate Your<br>Financial Data Flow</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <p class="hero-sub">
            Effortless reporting with a friendly guide. Upload laporan keuangan PDF,
            biarkan bot kirim angka ke Google Sheet <strong>"FINANCIAL_REPORT"</strong>
            dan menyimpan PDF-nya di Google Drive.
        </p>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
        <div class="upload-card">
            <div class="upload-title">Upload Financial PDF Report</div>
            <div class="upload-sub">
                Drag &amp; drop atau klik tombol di bawah (maks 20MB, PDF).
            </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        label="",
        type=["pdf"],
        key="pdf_uploader_main",
    )

    st.markdown("</div>", unsafe_allow_html=True)  # tutup upload-card

# =========================
# PROSES PDF
# =========================
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

if result:
    st.success("Selesai! ✅ Google Sheet & Google Drive sudah di-update.")
    st.json(result)
    if isinstance(result, dict) and result.get("drive_link"):
        st.markdown(
            f"[Buka file PDF di Google Drive]({result['drive_link']})",
            unsafe_allow_html=False,
        )

st.write("")

# =========================
# HOW IT WORKS
# =========================
st.markdown(
    '<div class="section-label">HOW IT WORKS</div><div class="section-divider"></div>',
    unsafe_allow_html=True,
)

how_it_works_path = "assets/how_it_works.png"
if os.path.exists(how_it_works_path):
    st.image(how_it_works_path, use_column_width=True)
else:
    st.info(
        "Tambahkan ilustrasi alur di **assets/how_it_works.png** "
        "untuk menampilkan gambar di sini."
    )

st.write("")

# =========================
# TIPS PENGGUNAAN
# =========================
st.markdown(
    '<div class="section-label">TIPS PENGGUNAAN</div><div class="section-divider"></div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="tips-card">
    <ul>
        <li>Pastikan format PDF mengikuti template laporan keuangan InHarmony.</li>
        <li>Kalau periodenya sama (misal <strong>Nov 2025</strong>), data P&amp;L / BS / Cash Flow akan diupdate di kolom periode yang sama.</li>
        <li>KPI untuk periode yang sama akan <strong>dioverwrite</strong>, tidak ditumpuk ulang.</li>
        <li>Simpan link Google Sheet &amp; Google Drive di bookmark untuk akses cepat.</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# FOOTER
# =========================
st.markdown(
    """
    <div class="footer-text">
        created by <span class="footer-highlight">xslsxcn</span> · Published 2026
    </div>
    """,
    unsafe_allow_html=True,
)
