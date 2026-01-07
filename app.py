# =========================
# IMPORTS
# =========================
import streamlit as st

# ganti ini sesuai file tempat process_pdf kamu berada
from main import process_pdf   # <-- SESUAIKAN JIKA PERLU


# =========================
# STYLE HELPER
# =========================
def inject_css():
    st.markdown(
        """
        <style>
        /* Hilangkan padding default di atas */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        /* Top nav bar */
        .top-nav {
            background: #0F172A; /* navy */
            color: white;
            padding: 0.8rem 1.5rem;
            border-radius: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.2rem;
        }
        .top-nav-left {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            font-size: 0.9rem;
            text-transform: uppercase;
        }
        .top-nav-tag {
            background: rgba(37, 99, 235, 0.15);
            border-radius: 999px;
            padding: 0.15rem 0.7rem;
            font-size: 0.75rem;
        }
        .top-nav-right {
            font-size: 0.8rem;
            opacity: 0.8;
        }

        /* Hero wrapper */
        .hero-wrapper {
            background: radial-gradient(circle at top left, #EFF6FF 0, #FFFFFF 50%, #E5E7EB 100%);
            border-radius: 1.5rem;
            padding: 1.8rem 1.8rem 1.4rem 1.8rem;
            border: 1px solid rgba(15,23,42,0.06);
            box-shadow: 0 18px 40px rgba(15,23,42,0.07);
            margin-bottom: 1.8rem;
        }

        .hero-title {
            font-size: 2.1rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 0.5rem;
        }

        .hero-subtitle {
            font-size: 0.98rem;
            color: #4B5563;
            max-width: 420px;
            margin-bottom: 1.1rem;
        }

        .hero-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.8rem;
            padding: 0.25rem 0.8rem;
            border-radius: 999px;
            background: rgba(22,163,74,0.08);
            color: #14532D;
            margin-bottom: 0.8rem;
        }

        .hero-pill span.dot {
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: #22C55E;
        }

        /* Upload card */
        .upload-card {
            background: rgba(255,255,255,0.88);
            backdrop-filter: blur(10px);
            border-radius: 1.2rem;
            border: 1px solid rgba(148,163,184,0.4);
            padding: 1.2rem 1.1rem 1.1rem 1.1rem;
            box-shadow: 0 10px 25px rgba(15,23,42,0.08);
            transition: all 0.18s ease-out;
        }
        .upload-card:hover {
            box-shadow: 0 16px 35px rgba(15,23,42,0.18);
            transform: translateY(-2px);
            border-color: rgba(37,99,235,0.45);
        }

        .upload-title {
            font-size: 0.95rem;
            font-weight: 600;
            color: #0F172A;
            margin-bottom: 0.3rem;
        }

        .upload-caption {
            font-size: 0.8rem;
            color: #6B7280;
            margin-bottom: 0.6rem;
        }

        /* Mengatur uploader bawaan Streamlit agar muat di card */
        .upload-card .stFileUploader {
            padding: 0.4rem 0.4rem 0.2rem 0.4rem;
            border-radius: 0.9rem;
            border: 1px dashed #BFDBFE;
            background: #F9FAFB;
        }

        /* Footer */
        .footer {
            text-align: center;
            font-size: 0.8rem;
            color: #6B7280;
            margin-top: 1.8rem;
        }
        .footer span.brand {
            font-weight: 600;
            color: #0F172A;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# STREAMLIT APP
# =========================
def main():
    st.set_page_config(
        page_title="Financial PDF → Google Sheet",
        page_icon="💹",
        layout="wide",
    )

    inject_css()

    # ========= TOP NAV =========
    with st.container():
        st.markdown(
            """
            <div class="top-nav">
              <div class="top-nav-left">
                <div style="width:22px;height:22px;border-radius:8px;background:#22C55E;display:flex;align-items:center;justify-content:center;">
                  <span style="font-size:13px;">🦆</span>
                </div>
                <span>Financial Report Upload</span>
                <span class="top-nav-tag">PDF → Google Sheet & Drive</span>
              </div>
              <div class="top-nav-right">
                inHARMONY • Automated reporting
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ========= HERO SECTION =========
    with st.container():
        st.markdown('<div class="hero-wrapper">', unsafe_allow_html=True)

        col_left, col_right = st.columns([1.3, 1], gap="large")

        # ---- Left: text ----
        with col_left:
            st.markdown(
                """
                <div class="hero-pill">
                  <span class="dot"></span>
                  Upload once · Sheet updates automatically
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="hero-title">Automate Your Financial Data Flow</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                """
                <div class="hero-subtitle">
                  Upload laporan keuangan dalam format PDF, dan biarkan bebek analis
                  favoritmu menyalin angka-angka ke Google Sheet & Google Drive — cepat,
                  konsisten, dan bebas typo.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <ul style="padding-left:1.1rem;margin-top:0.2rem;color:#4B5563;font-size:0.86rem;">
                  <li>Support P&L, Balance Sheet, Cash Flow, dan KPI Result</li>
                  <li>Update <b>FINANCIAL_REPORT</b> secara otomatis per periode</li>
                  <li>PDF tersimpan rapi di folder Financial Reports di Google Drive</li>
                </ul>
                """,
                unsafe_allow_html=True,
            )

        # ---- Right: duck + uploader ----
        with col_right:
            # Bebek
            st.image("assets/duck.png", width=210, caption=None)

            st.markdown('<div class="upload-card">', unsafe_allow_html=True)
            st.markdown(
                '<div class="upload-title">Upload PDF laporan</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="upload-caption">Limit 20MB per file · Format: PDF</div>',
                unsafe_allow_html=True,
            )

            uploaded_file = st.file_uploader(
                label="",
                type=["pdf"],
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # close hero-wrapper

    # ========= PROCESSING =========
    result = None

    if uploaded_file is not None:
        pdf_path = "report.pdf"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        with st.spinner("Memproses PDF, mengupdate Google Sheet & mengupload ke Drive..."):
            try:
                # process_pdf milikmu yang sudah jalan (mengembalikan dict)
                result = process_pdf(pdf_path)
            except Exception as e:
                st.error("Terjadi error saat memproses PDF / update Google.")
                st.exception(e)
                return

        st.success("Selesai! ✅ Google Sheet & Google Drive sudah di-update.")

    # ========= SUMMARY =========
    if result:
        st.subheader("Ringkasan hasil")
        st.json(result)

        drive_link = result.get("drive_link")
        if drive_link:
            st.markdown(
                f"📎 **File PDF di Google Drive:** "
                f"[Buka file]({drive_link})",
                unsafe_allow_html=False,
            )

    # ========= FOOTER =========
    st.markdown(
        """
        <div class="footer">
          created by <span class="brand">xlsxcen</span> · Published 2026
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main()
