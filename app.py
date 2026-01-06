# =========================
# IMPORTS
# =========================
import streamlit as st
import os
from datetime import datetime

from main import process_pdf   # ⬅️ WAJIB ADA (sudah kita siapkan di main.py)

# =========================
# CONFIG
# =========================
UPLOAD_DIR = "uploads"
PDF_TARGET = "report.pdf"

os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(
    page_title="Financial PDF → Google Sheet",
    page_icon="📊",
    layout="centered"
)

# =========================
# UI HEADER
# =========================
st.title("📊 Financial Report Automation")
st.caption("Upload PDF → Auto Parse → Auto Update Google Sheet")

st.divider()

# =========================
# FILE UPLOAD
# =========================
uploaded_file = st.file_uploader(
    "📎 Upload Financial Report (PDF)",
    type=["pdf"],
    accept_multiple_files=False
)

if uploaded_file:
    now = datetime.now()
    display_name = uploaded_file.name

    saved_path = os.path.join(UPLOAD_DIR, display_name)

    with open(saved_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success(f"✅ File uploaded: {display_name}")

    st.info(
        "📌 File akan diproses dan otomatis "
        "dikirim ke Google Sheet **FINANCIAL_REPORT**"
    )

    st.divider()

    # =========================
    # PROCESS BUTTON
    # =========================
    if st.button("🚀 Process & Update Google Sheet"):
        with st.spinner("⏳ Processing PDF, please wait..."):
            try:
                # 🔁 Rename / replace ke nama yang dibaca engine
                if os.path.exists(PDF_TARGET):
                    os.remove(PDF_TARGET)

                os.replace(saved_path, PDF_TARGET)

                # ▶️ RUN CORE PROCESS
                result = process_pdf(PDF_TARGET)

                st.success("🎉 Processing completed successfully!")

                # =========================
                # RESULT SUMMARY
                # =========================
                st.subheader("📈 Processing Summary")
                st.write(f"**Period:** {result['period']}")
                st.write(f"• P&L rows: {result['pl_rows']}")
                st.write(f"• Balance Sheet rows: {result['bs_rows']}")
                st.write(f"• Cash Flow rows: {result['cf_rows']}")
                st.write(f"• KPI rows appended: {result['kpi_rows']}")

                st.success("✅ Data successfully updated in Google Sheet")

            except Exception as e:
                st.error("❌ Processing failed")
                st.exception(e)

else:
    st.info("⬆️ Upload PDF untuk memulai proses")

st.divider()
st.caption("Powered by Python • pdfplumber • Streamlit • Google Sheets API")
