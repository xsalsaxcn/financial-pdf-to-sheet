import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime

# Scope Drive
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Folder di MY DRIVE kamu tempat laporan disimpan
# Pakai folder "Financial Reports" yang sekarang sudah ada
# Ambil ID dari URL:
# https://drive.google.com/drive/folders/XXXXXXXXXXXX  -> pakai "XXXXXXXXXXXX"
ROOT_FOLDER_ID = "GANTI_DENGAN_FOLDER_ID_FINANCIAL_REPORTS"


def get_drive_service():
    """
    Buat Drive client sebagai USER (bukan service account)
    pakai client_id, client_secret, refresh_token dari st.secrets[gcp_oauth]
    """
    oauth = st.secrets["gcp_oauth"]

    creds = Credentials(
        token=None,  # akan otomatis di-refresh dari refresh_token
        refresh_token=oauth["refresh_token"],
        token_uri=oauth["token_uri"],
        client_id=oauth["client_id"],
        client_secret=oauth["client_secret"],
        scopes=SCOPES,
    )

    return build("drive", "v3", credentials=creds)


def get_or_create_folder(service, name: str, parent_id: str) -> str:
    """
    Cari folder bernama 'name' di dalam parent_id.
    Kalau tidak ada, buat baru.
    """
    query = (
        f"name='{name}' and "
        f"mimeType='application/vnd.google-apps.folder' and "
        f"'{parent_id}' in parents and trashed=false"
    )

    result = (
        service.files()
        .list(
            q=query,
            spaces="drive",
            fields="files(id, name)",
        )
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

    folder = (
        service.files()
        .create(
            body=folder_metadata,
            fields="id",
        )
        .execute()
    )

    return folder["id"]


def upload_pdf_to_drive(pdf_path: str, period: str) -> str:
    """
    Upload PDF ke My Drive user,
    struktur folder:
        ROOT_FOLDER /
          <tahun> /
            <MM_Mmm> /
              PL_Mmm_YYYY.pdf

    Return: webViewLink (URL ke file di Drive)
    """
    service = get_drive_service()

    # period contoh: "Nov 2025" atau "November 2025"
    month, year = period.split()
    try:
        month_num = datetime.strptime(month, "%b").month  # "Nov"
    except ValueError:
        month_num = datetime.strptime(month, "%B").month  # "November"

    month_folder_name = f"{month_num:02d}_{month}"

    year_folder_id = get_or_create_folder(service, year, ROOT_FOLDER_ID)
    month_folder_id = get_or_create_folder(service, month_folder_name, year_folder_id)

    file_name = f"PL_{month}_{year}.pdf"

    file_metadata = {
        "name": file_name,
        "parents": [month_folder_id],
    }

    media = MediaFileUpload(pdf_path, mimetype="application/pdf")

    uploaded = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
        )
        .execute()
    )

    # Kalau mau bisa diakses siapa saja yang punya link, bisa buka komentar ini:
    # service.permissions().create(
    #     fileId=uploaded["id"],
    #     body={"role": "reader", "type": "anyone"},
    # ).execute()

    return uploaded["webViewLink"]
