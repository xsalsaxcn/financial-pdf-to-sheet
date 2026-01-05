import streamlit as st
import os
from datetime import datetime
from main import process_pdf   # ← ini penting

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="Financial PDF Upload",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Financial Report Upload")
st.caption("Upload PDF → Auto Parse → Google Sheet")

uploaded_file = st.file_uploader(
    "Upload Financial Report (PDF)",
    type=["pdf"]
)

if uploaded_file:
    filepath = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

    with open(filepath, "wb") as f:
        f.write(uploaded_file.read())

    st.success(f"✅ File uploaded: {uploaded_file.name}")

    if st.button("🚀 Process & Send to Google Sheet"):
        with st.spinner("Processing PDF..."):
            success, message = process_pdf(filepath)

        if success:
            st.success(message)
        else:
            st.error(message)
