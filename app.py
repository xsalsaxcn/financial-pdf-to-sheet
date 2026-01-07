# app.py

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
# GLOBAL CSS
# =========================
def inject_css():
    st.markdown(
        """
        <style>
        /* Background keseluruhan */
        .stApp {
            background: radial-gradient(circle at top, #14284b 0, #071324 45%, #040814 100%);
            color: #0f172a;
        }

        /* Container utama supaya lebih sempit & center */
        .block-container {
            max-width: 1150px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        /* Top nav bar */
        .top-nav {
            background: #050a16;
            color: #e5e7eb;
            padding: 0.6rem 1.6rem;
            border-radius: 0 0 18px 18px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 14px 35px rgba(0,0,0,0.45);
        }
        .top-nav-title {
            font-weight: 600;
        }
        .top-nav-sub {
            font-size: 0.83rem;
            opacity: 0.9;
        }

        /* HERO CARD */
        .hero-card {
            margin-top: 1.8rem;
            background: #f9fafb;
            border-radius: 24px;
            padding: 2.2rem 2.4rem 2.0rem 2.4rem;
            box-shadow:
                0 25px 60px rgba(15,23,42,0.45),
                0 0 0 1px rgba(15,23,42,0.06);
        }
        .hero-title {
            font-size: 2.15rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 0.45rem;
        }
        .hero-subtitle {
            font-size: 0.98rem;
            color: #4b5563;
            max-width: 560px;
            margin-bottom: 1.6rem;
        }

        .hero-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #0f172a;
            color: #e5e7eb;
            font-size: 0.75rem;
            padding: 0.25rem 0.9rem;
            border-radius: 999px;
            margin-bottom: 1rem;
        }
        .hero-pill-dot {
            width: 7px;
            height: 7px;
            border-radius: 999px;
            background: #22c55e;
        }

        /* Card upload di kanan */
        .upload-card {
            background: #0b172a;
            border-radius: 20px;
            padding: 1.3rem 1.3rem 1.5rem 1.3rem;
            box-shadow:
                0 20px 50px rgba(15,23,42,0.7),
                0 0 0 1px rgba(148,163,184,0.25);
            border: 1px solid rgba(148,163,184,0.5);
        }
        .upload-title {
            color: #e5e7eb;
            font-weight: 600;
            margin-bottom: 0.4rem;
        }
        .upload-sub {
            font-size: 0.82rem;
            color: #9ca3af;
            margin-bottom: 0.8rem;
        }

        /* Membungkus widget uploader supaya menyatu */
        .upload-inner {
            background: #f9fafb;
            border-radius: 999px;
            padding: 0.15rem 0.9rem;
        }

        /* Banner flow (cloud -> duck -> G) */
        .flow-card {
            margin-top: 1.6rem;
            background: linear-gradient(135deg, #020617 0, #020617 45%, #020617 100%);
            border-radius: 22px;
            padding: 1.1rem 1.5rem 1.3rem 1.5rem;
            box-shadow: 0 20px 55px rgba(15,23,42,0.7);
            border: 1px solid rgba(148,163,184,0.35);
        }
        .flow-caption {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: #9ca3af;
            margin-bottom: 0.35rem;
        }

        /* Tips section */
        .tips-card {
            margin-top: 1.8rem;
            background: rgba(15,23,42,0.92);
            border-radius: 999px;
            padding: 0.9rem 1.8rem;
            color: #e5e7eb;
            font-size: 0.9rem;
            box-shadow: 0 16px 40px rgba(15,23,42,0.7);
        }
        .tips-title {
            font-weight: 600;
            margin-bottom: 0.25rem;
        }
        .tips-ul {
            margin: 0.3rem 0 0.1rem 0;
            padding-left: 1.1rem;
        }

        /* Footer */
        .footer {
            margin-top: 2.1rem;
            text-align: center;
            font-size: 0.8rem;
            color: #9ca3af;
            opacity: 0.9;
        }

        /* Compress default spacing antar elemen */
        .element-container:has(> .stMarkdown) {
            margin-bottom: 0.4rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# LAYOUT
# =========================
def main():
    inject_css()

    # ---------- TOP NAV ----------
    st.markdown(
        """
        <div class="top-nav">
            <div class="top-nav-title">Financial Report Upload</div>
            <div class="top-nav-sub"> • Upload PDF → Auto Parse → Google Sheet & Drive</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- HERO CARD ----------
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)

    col_left, col_right = st.columns([1.35, 1])

    # LEFT: title + duck
    with col_left:
        st.markdown(
            """
            <div class="hero-pill">
                <div class="hero-pill-dot"></div>
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
                biarkan bot kirim ke Google Sheet <b>"FINANCIAL_REPORT"</b> dan PDF-nya
                otomatis tersimpan di Google Drive.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Duck kecil di kiri
        st.image("assets/duck.png", width=200)

    # RIGHT: upload card
    uploaded_file = None
    with col_right:
        st.markdown('<div class="upload-card">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="upload-title">Drag and drop file here</div>
            <div class="upload-sub">Limit 20MB per file • PDF</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="upload-inner">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(" ", type=["pdf"], label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)  # close upload-card

    st.markdown("</div>", unsafe_allow_html=True)  # close hero-card

    # ---------- FLOW BANNER ----------
    st.markdown('<div class="flow-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="flow-caption">How it works</div>',
        unsafe_allow_html=True,
    )
    st.image("assets/flow_banner.png", use_column_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- PROCESS UPLOADED FILE ----------
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
    st.markdown('<div class="tips-card">', unsafe_allow_html=True)
    st.markdown('<div class="tips-title">Tips penggunaan</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <ul class="tips-ul">
            <li>Pastikan format PDF mengikuti template laporan keuangan InHarmony.</li>
            <li>Kalau periodenya sama (misal <b>Nov 2025</b>), data P&amp;L / BS / Cash Flow akan diupdate di kolom periode yang sama.</li>
            <li>KPI untuk periode yang sama akan <b>dioverwrite</b>, tidak ditumpuk ulang.</li>
            <li>Simpan link Google Sheet &amp; Google Drive di bookmark untuk akses cepat.</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- RESULT JSON + DRIVE LINK ----------
    if result is not None:
        st.subheader("Ringkasan hasil")
        st.json(result)

        drive_link = result.get("drive_link")
        if drive_link:
            st.markdown(
                f"**File PDF di Google Drive:** "
                f"[Buka file]({drive_link})",
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
