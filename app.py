# app.py
import os
import streamlit as st
from main import process_pdf  # pastikan main.py punya fungsi process_pdf(pdf_path)

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Financial Report Upload · InHarmony",
    page_icon="📊",
    layout="wide",
)


# =========================
# GLOBAL STYLES
# =========================
APP_CSS = """
<style>
/* APP BACKGROUND */
.stApp {
    background: radial-gradient(circle at 20% 0%, #1e293b 0, #020617 40%, #020617 100%);
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Main body width */
.block-container {
    max-width: 1200px;
}

/* Global text colors (JANGAN include span di sini biar st.json aman) */
h1, h2, h3, h4, h5, h6,
.stMarkdown, .stText, .stTooltipContent, label, p, li {
    color: #e5e7eb !important;
}

/* Link */
a {
    color: #38bdf8;
}
a:hover {
    color: #7dd3fc;
}

/* TOP NAV BAR */
.top-nav {
    margin: 0.5rem 0 1.75rem 0;
    padding: 0.6rem 1rem;
    border-radius: 999px;
    background: linear-gradient(90deg, #020617, #020617);
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.55);
    display: flex;
    align-items: center;
    gap: 0.7rem;
    font-size: 0.78rem;
    color: #cbd5f5;
}
.top-nav strong {
    color: #e5e7ff;
}

/* Status pill */
.pill-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    background: rgba(22, 163, 74, 0.15);
    border: 1px solid rgba(34, 197, 94, 0.65);
    color: #bbf7d0;
    font-size: 0.7rem;
    margin-bottom: 0.7rem;
}
.pill-dot {
    width: 6px;
    height: 6px;
    border-radius: 999px;
    background: #22c55e;
}

/* HERO TITLE */
.hero-title {
    font-size: 2.3rem;
    font-weight: 800;
    letter-spacing: 0.02em;
    color: #f9fafb;
    margin-bottom: 0.5rem;
}
.hero-subtitle {
    font-size: 0.92rem;
    line-height: 1.5;
    color: #cbd5f5;
}

/* UPLOAD CARD WRAPPER (kanan) */
.upload-wrapper {
    display: flex;
    justify-content: flex-end;
    align-items: stretch;
    margin-top: 0.25rem;
}

/* Card luar */
.upload-card {
    width: 100%;
    padding: 0.9rem 1.3rem 1.05rem 1.3rem;
    border-radius: 1.1rem;
    background:
        radial-gradient(circle at 0% -20%, rgba(56, 189, 248, 0.35), transparent 55%),
        radial-gradient(circle at 120% 120%, rgba(248, 250, 252, 0.05), transparent 60%),
        linear-gradient(135deg, #020617 0%, #020617 45%, #020617 100%);
    border: 1px solid rgba(148, 163, 184, 0.55);
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9);
}

/* Card header text */
.upload-card-title {
    font-size: 0.98rem;
    font-weight: 600;
    color: #f9fafb;
    margin-bottom: 0.05rem;
}
.upload-card-subtitle {
    font-size: 0.78rem;
    color: #cbd5f5;
    margin-bottom: 0.75rem;
}

/* FILE UPLOADER STYLING INSIDE CARD */
.upload-inner {
    border-radius: 0.9rem;
    border: 1px dashed rgba(148, 163, 184, 0.8);
    background: radial-gradient(circle at 10% 0%, rgba(248, 250, 252, 0.16), rgba(15, 23, 42, 0.9));
    padding: 0.65rem 0.75rem;
}

/* Hide original label text (kita styling sendiri) */
.upload-inner label {
    font-size: 0.85rem;
}

/* Target komponen uploader */
.upload-inner div[data-testid="stFileUploader"] {
    background: #f9fafb;
    border-radius: 0.75rem;
    padding: 0.6rem 0.8rem;
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.9);
}

/* Layout internal uploader: cloud + text + button */
.upload-inner div[data-testid="stFileUploader"] > div:first-child {
    gap: 0.5rem;
}

/* Cloud icon */
.upload-inner svg {
    width: 32px;
    height: 32px;
}

/* Text di dalam uploader */
.upload-inner div[data-testid="stFileUploader"] span {
    color: #0f172a !important;
    font-size: 0.8rem !important;
}

/* Tombol Browse files */
.upload-inner button {
    background: linear-gradient(135deg, #f59e0b, #f97316);
    color: #0f172a;
    font-weight: 600;
    border-radius: 999px;
    padding: 0.4rem 1.2rem;
    border: none;
}
.upload-inner button:hover {
    background: linear-gradient(135deg, #facc15, #f97316);
    color: #020617;
}

/* SECTION TITLE */
.section-title {
    margin-top: 2.4rem;
    margin-bottom: 0.3rem;
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #9ca3af;
}
.section-divider {
    width: 100%;
    height: 0.9rem;
    border-radius: 999px;
    background: radial-gradient(circle at 15% 0%, rgba(148, 163, 184, 0.8), transparent 55%),
                linear-gradient(90deg, rgba(15, 23, 42, 0.95), rgba(15, 23, 42, 0.7));
    margin-bottom: 0.9rem;
}

/* HOW IT WORKS placeholder */
.how-placeholder {
    padding: 0.85rem 1.1rem;
    border-radius: 0.75rem;
    border: 1px dashed rgba(148, 163, 184, 0.7);
    font-size: 0.8rem;
    color: #d1d5db;
    background: rgba(15, 23, 42, 0.75);
}

/* TIPS CARD */
.tips-card {
    margin-top: 0.4rem;
    padding: 1.1rem 1.15rem 0.9rem 1.15rem;
    border-radius: 1rem;
    border: 1px solid rgba(148, 163, 184, 0.7);
    background: radial-gradient(circle at 0% -40%, rgba(248, 250, 252, 0.1), transparent 55%),
                rgba(15, 23, 42, 0.92);
    box-shadow: 0 22px 55px rgba(0, 0, 0, 0.9);
    font-size: 0.85rem;
    color: #e5e7eb;
}
.tips-card ul {
    padding-left: 1.2rem;
    margin-bottom: 0.2rem;
}
.tips-card li {
    margin-bottom: 0.25rem;
    color: #e5e7eb !important;
}

/* FOOTER */
.footer {
    margin-top: 1.8rem;
    text-align: center;
    font-size: 0.75rem;
    color: #9ca3af;
}
.footer span {
    color: #e5e7eb;
}

/* SUCCESS MESSAGE TWEAK */
div[data-testid="stToastContainer"] div[role="alert"] {
    font-size: 0.85rem;
}

/* JSON RESULT CARD */
div[data-testid="stJson"] {
    background: rgba(15, 23, 42, 0.98);
    border-radius: 0.9rem;
    padding: 0.9rem 1.1rem;
    border: 1px solid rgba(148, 163, 184, 0.7);
    box-shadow: 0 18px 40px rgba(0, 0, 0, 0.7);
}
div[data-testid="stJson"] pre,
div[data-testid="stJson"] code,
div[data-testid="stJson"] span {
    color: #e5e7eb !important;
    font-size: 0.85rem !important;
}
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)


# =========================
# STREAMLIT LAYOUT
# =========================
def main():
    # Top nav
    st.markdown(
        """
        <div class="top-nav">
            <strong>Financial Report Upload</strong>
            <span>· Upload PDF → Auto Parse → Google Sheet & Drive</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Status pill
    st.markdown(
        """
        <div class="pill-badge">
            <div class="pill-dot"></div>
            <span>InHarmony Financial Automation</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # HERO SECTION (title + upload)
    hero_left, hero_right = st.columns([1.1, 1])

    with hero_left:
        st.markdown(
            '<div class="hero-title">Automate Your Financial Data Flow</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <p class="hero-subtitle">
            Effortless reporting with a friendly guide. Upload laporan keuangan PDF,
            biarkan bot mengirim angka ke Google Sheet <strong>"FINANCIAL_REPORT"</strong>
            dan menyimpan PDF-nya di Google Drive.
            </p>
            """,
            unsafe_allow_html=True,
        )

    with hero_right:
        st.markdown('<div class="upload-wrapper"><div class="upload-card">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="upload-card-title">Upload Financial PDF Report</div>
            <div class="upload-card-subtitle">
                Drag &amp; drop atau klik tombol di bawah (maks 20MB, PDF).
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Uploader inside styled wrapper
        st.markdown('<div class="upload-inner">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drag and drop file here",
            type=["pdf"],
            label_visibility="collapsed",
            key="pdf_uploader",
        )
        st.markdown("</div></div></div>", unsafe_allow_html=True)

    st.write("")  # small spacer

    # Jika user upload file → proses
    result = None
    if uploaded_file is not None:
        # Simpan file sementara
        pdf_path = "report.pdf"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        with st.spinner("Memproses PDF dan meng-update Google Sheet & Google Drive..."):
            try:
                result = process_pdf(pdf_path)
            except Exception as e:
                st.error("Terjadi error saat memproses PDF / update Google.")
                st.exception(e)

        if result:
            st.success("Selesai! ✅ Google Sheet & Google Drive sudah di-update.")
            st.markdown("##### Ringkasan hasil")
            st.json(result)

            # Kalau ada drive_link di result → tampilkan link
            drive_link = result.get("drive_link")
            if isinstance(drive_link, dict):
                drive_url = drive_link.get("link")
            else:
                drive_url = drive_link

            if drive_url:
                st.markdown(
                    f"**File PDF di Google Drive:** "
                    f"[Buka file]({drive_url})",
                    unsafe_allow_html=True,
                )

    # =========================
    # HOW IT WORKS
    # =========================
    st.markdown('<div class="section-title">HOW IT WORKS</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    how_path = os.path.join("assets", "how_it_works.png")
    if os.path.exists(how_path):
        st.image(how_path, use_column_width=True)
    else:
        st.markdown(
            '<div class="how-placeholder">'
            'Tambahkan ilustrasi alur di <code>assets/how_it_works.png</code> untuk menampilkan gambar di sini.'
            "</div>",
            unsafe_allow_html=True,
        )

    # =========================
    # TIPS PENGGUNAAN
    # =========================
    st.markdown('<div class="section-title">TIPS PENGGUNAAN</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="tips-card">', unsafe_allow_html=True)
    st.markdown(
        """
        <ul>
            <li>Pastikan format PDF mengikuti template laporan keuangan InHarmony.</li>
            <li>Kalau periodenya sama (misal <strong>Nov 2025</strong>), data P&amp;L / BS / Cash Flow akan diupdate di kolom periode yang sama.</li>
            <li>KPI untuk periode yang sama akan <strong>dioverwrite</strong>, tidak ditumpuk ulang.</li>
            <li>Simpan link Google Sheet &amp; Google Drive di bookmark untuk akses cepat.</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # FOOTER
    # =========================
    st.markdown(
        """
        <div class="footer">
            created by <span>xslsxcn</span> · Published 2026
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
