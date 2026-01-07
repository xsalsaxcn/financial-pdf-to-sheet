# =========================
# UPLOAD PDF TO GOOGLE DRIVE
# =========================
import json
from datetime import datetime

import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =========================
# CONFIG
# =========================
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Folder utama di Drive tempat semua laporan disimpan
ROOT_FOLDER_ID = "12934i5FjV9OA96tU3OXBhmyHpGflXjXF"  # <- pastikan folder ini di-share ke service account!


# =========================
# AUTH
# =========================
def get_drive_service():
    """
    Buat client Google Drive pakai service account
    yang ada di st.secrets[gcp_service_account].json
    """

    info = json.loads(st.secrets["gcp_service_account"]["json"])

    creds = Credentials.from_service_account_info(
        info,
        scopes=SCOPES,
    )

    return build("drive", "v3", credentials=creds)


# =========================
# FIND OR CREATE FOLDER
# =========================
def get_or_create_folder(service, name, parent_id):
    query = (
        f"name='{name}' and "
        f"mimeType='application/vnd.google-apps.folder' and "
        f"'{parent_id}' in parents and trashed=false"
    )

    result = (
        service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
    )

    files = result.get("files", [])
    if files:
        return files[0]["id"]

    folder_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }

    folder = service.files().create(body=folder_metadata, fields="id").execute()
    return folder["id"]


# =========================
# UPLOAD PDF
# =========================
def upload_pdf_to_drive(pdf_path: str, period: str) -> str:
    """
    Upload PDF ke Drive dengan struktur folder:
      ROOT_FOLDER_ID /
        <year> /
          <MM_Mmm> /
            PL_Mmm_YYYY.pdf

    pdf_path : path lokal PDF
    period   : "Nov 2025"

    Return: webViewLink (string) ke file di Google Drive
    """

    service = get_drive_service()

    # ===== PERIOD =====
    month, year = period.split()
    month_num = datetime.strptime(month, "%b").month
    month_folder_name = f"{month_num:02d}_{month}"

    # ===== FOLDER STRUCTURE =====
    year_folder_id = get_or_create_folder(service, year, ROOT_FOLDER_ID)
    month_folder_id = get_or_create_folder(
        service, month_folder_name, year_folder_id
    )

    # ===== FILE NAME =====
    file_name = f"PL_{month}_{year}.pdf"

    file_metadata = {
        "name": file_name,
        "parents": [month_folder_id],
    }

    media = MediaFileUpload(pdf_path, mimetype="application/pdf")

    uploaded = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id, webViewLink")
        .execute()
    )

    # Kalau mau file bisa diakses siapa saja dengan link, aktifkan block ini:
    # service.permissions().create(
    #     fileId=uploaded["id"],
    #     body={"role": "reader", "type": "anyone"},
    # ).execute()

    return uploaded["webViewLink"]
