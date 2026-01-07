# app.py
# UI untuk Financial PDF -> Google Sheet + Drive
# Backend parsing & update ada di main.process_pdf

import os
import streamlit as st
from main import process_pdf  # pastikan main.py punya fungsi process_pdf(pdf_path)

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Financial Report Upload",
    page_icon="📄",
    layout="wide",
)

# =========================
# CUSTOM CSS
# =========================
CUSTOM_CSS = """
<style>
/* --------- GLOBAL LAYOUT --------- */
.stApp {
  background: radial-gradient(circle at top left, #263a63 0%, #111827 45%, #020617 100%);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
}

/* Container lebar */
.block-container {
  padding-top: 0.5rem;
  padding-bottom: 2.5rem;
  max-width: 1100px;
}

/* --------- TOP NAV / HEADER STRIP --------- */
.top-nav {
  background: rgba(3, 7, 18, 0.96);
  border-radius: 0 0 18px 18px;
  padding: 0.7rem 1.5rem;
  margin: -1rem -1.5rem 1.25rem -1.5rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.4);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.9);
  font-size: 0.85rem;
}
.top-nav span.brand {
  font-weight: 600;
  color: #e5edff;
}
.top-nav span.breadcrumb {
  color: #9ca3af;
}

/* --------- HERO AREA --------- */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.08);
  border: 1px solid rgba(34, 197, 94, 0.4);
  color: #bbf7d0;
  font-size: 0.72rem;
  margin-bottom: 0.8rem;
}

.hero-title {
  font-size: 2.25rem;
  line-height: 1.15;
  font-weight: 700;
  color: #f9fbff;
  margin-bottom: 0.25rem;
}

.hero-subtitle {
  font-size: 0.95rem;
  color: #d5e3ff;
  max-width: 430px;
}

/* Biar teks default di halaman cukup terang di background gelap */
.main-text p, .main-text li {
  color: #dde7ff;
}

/* --------- UPLOAD PANEL --------- */
.upload-panel {
  background: radial-gradient(circle at top left, #f5f8ff 0%, #ffffff 45%, #edf2ff 100%);
  border-radius: 18px;
  padding: 1.15rem 1.25rem 1.3rem;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.45);
}

.upload-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 0.15rem;
}

.upload-subtitle {
  font-size: 0.78rem;
  color: #4b5563;
  margin-bottom: 0.75rem;
}

/* Native Streamlit uploader styling */
div[data-testid="stFileUploader"] {
  margin-bottom: 0;
}

div[data-testid="stFileUploaderDropzone"] {
  border-radius: 14px;
  padding: 1.35rem 1.4rem;
  border: 2px dashed rgba(59, 130, 246, 0.5);
  background: linear-gradient(135deg, #ffffff 0%, #f3f6ff 55%, #e5efff 100%);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.3);
}

/* Besarin icon cloud */
div[data-testid="stFileUploaderDropzone"] svg {
  width: 46px;
  height: 46px;
}

/* Teks di dalam dropzone tetap gelap (karena background-nya terang) */
div[data-testid="stFileUploaderDropzone"] span {
  color: #111827 !important;
}

/* --------- SECTION TITLES & DIVIDER --------- */
.section-title {
  font-size: 0.9rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #9fb4ff;
  margin-top: 2.75rem;
  margin-bottom: 0.5rem;
}

.section-divider {
  height: 7px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(148, 163, 255, 0.75), rgba(56, 189, 248, 0.15));
  margin-bottom: 1.2rem;
}

/* --------- HOW IT WORKS IMAGE --------- */
.how-card {
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.35);
}

/* --------- TIPS CARD --------- */
.tips-card {
  background: rgba(15, 23, 42, 0.88);
  border-radius: 18px;
  padding: 1.3rem 1.6rem 1.25rem;
  border: 1px solid rgba(148, 163, 184, 0.5);
  box-shadow: 0 14px 38px rgba(15, 23, 42, 0.85);
  font-size: 0.9rem;
}

.tips-card ul {
  padding-left: 1.1rem;
  margin-bottom: 0;
}

.tips-card li {
  color: #e4edff;
  margin-bottom: 0.45rem;
}

/* --------- RESULT CARD --------- */
.result-card {
  margin-top: 1.3rem;
  background: rgba(15, 23, 42, 0.9);
  border-radius: 16px;
  padding: 1rem 1.2rem;
  border: 1px solid rgba(148, 163, 184, 0.5);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.8);
  font-size: 0.85rem;
}

/* --------- FOOTER --------- */
.footer {
  margin-top: 2.3rem;
  font-size: 0.7rem;
  color: #9ca3af;
  text-align: center;
}
.footer span {
  color: #e5edff;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =========================
# MAIN APP
# =========================
def main():
    # ---------- Top nav ----------
    st.markdown(
        """
        <div class="top-nav">
          <span class="brand">Financial Report Upload</span>
          <span class="breadcrumb"> · Upload PDF → Auto Parse → Google Sheet & Drive</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        col_left, col_right = st.columns([1.3, 1])

        with col_left:
            st.markdown('<div class="badge">• InHarmony Financial Automation</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="main-text">'
                '<h1 class="hero-title">Automate Your<br/>Financial Data Flow</h1>'
                '<p class="hero-subtitle">'
                'Effortless reporting with a friendly guide. Upload laporan keuangan PDF, '
                'biarkan bot kirim angka ke Google Sheet <b>"FINANCIAL_REPORT"</b> '
                'dan menyimpan PDF-nya di Google Drive.'
                '</p>'
                '</div>',
                unsafe_allow_html=True,
            )

        with col_right:
            st.markdown('<div class="upload-panel">', unsafe_allow_html=True)
            st.markdown(
                '<p class="upload-title">Upload Financial PDF Report</p>'
                '<p class="upload-subtitle">Drag & drop atau klik tombol di bawah (maks 20MB, PDF).</p>',
                unsafe_allow_html=True,
            )

            uploaded_file = st.file_uploader(
                "Upload Financial PDF Report",
                type=["pdf"],
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)

    result = None

    if uploaded_file is not None:
        # Simpan PDF sementara
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
            finally:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

        st.success("Selesai! ✅ Google Sheet & Google Drive sudah di-update.")

        if result:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown("**Ringkasan hasil**", unsafe_allow_html=True)
            st.json(result)

            drive_link = result.get("drive_link")
            if isinstance(drive_link, dict):
                drive_link = drive_link.get("link")

            if drive_link:
                st.markdown(
                    f'📁 File PDF di Google Drive: '
                    f'<a href="{drive_link}" target="_blank">Buka file</a>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

    # ---------- HOW IT WORKS ----------
    st.markdown('<div class="section-title">HOW IT WORKS</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    how_img_path = "assets/how_it_works.png"  # sesuaikan nama file kamu
    if os.path.exists(how_img_path):
        st.markdown('<div class="how-card">', unsafe_allow_html=True)
        st.image(how_img_path, use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Tambahkan ilustrasi alur di `assets/how_it_works.png` untuk menampilkan gambar di sini.")

    # ---------- TIPS ----------
    st.markdown('<div class="section-title">TIPS PENGGUNAAN</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    tips_html = """
    <div class="tips-card main-text">
      <ul>
        <li>Pastikan format PDF mengikuti template laporan keuangan InHarmony.</li>
        <li>Kalau periodenya sama (misal <b>Nov 2025</b>), data P&amp;L / BS / Cash Flow akan diupdate di kolom periode yang sama.</li>
        <li>KPI untuk periode yang sama akan <b>dioverwrite</b>, tidak ditumpuk ulang.</li>
        <li>Simpan link Google Sheet &amp; Google Drive di bookmark untuk akses cepat.</li>
      </ul>
    </div>
    """
    st.markdown(tips_html, unsafe_allow_html=True)

    # ---------- FOOTER ----------
    st.markdown(
        '<div class="footer">created by <span>xslsxcn</span> · Published 2026</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
