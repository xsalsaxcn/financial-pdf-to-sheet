import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# =========================
# CONFIG
# =========================
CREDENTIALS_FILE = "credentials.json"

SCOPES = [
    "https://www.googleapis.com/auth/drive"
]

# ROOT FOLDER (punya kamu)
ROOT_FOLDER_ID = "12934i5FjV9OA96tU3OXBhmyHpGflXjXF"


# =========================
# INTERNAL: CONNECT DRIVE
# =========================
def connect_drive():
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


# =========================
# INTERNAL: GET OR CREATE FOLDER
# =========================
def get_or_create_folder(service, name, parent_id):
    query = (
        f"name='{name}' and "
        f"'{parent_id}' in parents and "
        f"mimeType='application/vnd.google-apps.folder' and "
        f"trashed=false"
    )

    results = service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()

    folders = results.get("files", [])
    if folders:
        return folders[0]["id"]

    folder_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }

    folder = service.files().create(
        body=folder_metadata,
        fields="id"
    ).execute()

    return folder["id"]


# =========================
# PUBLIC: UPLOAD PDF
# =========================
def upload_pdf_to_drive(local_pdf_path: str, period: str):
    """
    local_pdf_path : path ke file PDF (misal: report.pdf)
    period         : "Nov 2025"

    RETURN:
    - Google Drive file link
    """

    if not os.path.exists(local_pdf_path):
        raise FileNotFoundError(f"PDF not found: {local_pdf_path}")

    service = connect_drive()

    # ===== PARSE PERIOD =====
    try:
        month, year = period.split()
    except ValueError:
        raise ValueError("Period format harus: 'Nov 2025'")

    # ===== FOLDER STRUCTURE =====
    year_folder_id = get_or_create_folder(
        service,
        year,
        ROOT_FOLDER_ID
    )

    month_folder_id = get_or_create_folder(
        service,
        month,
        year_folder_id
    )

    # ===== FILE NAME =====
    filename = f"PL_{month}_{year}.pdf"

    media = MediaFileUpload(
        local_pdf_path,
        mimetype="application/pdf",
        resumable=True
    )

    file_metadata = {
        "name": filename,
        "parents": [month_folder_id]
    }

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    return uploaded["webViewLink"]
