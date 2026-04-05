"""Google Drive storage integration for property documents."""
import io
import json
import logging
from typing import Tuple, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from app.config import settings

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]


class GoogleDriveService:
    def __init__(self):
        creds_json = settings.google_service_account_json
        if creds_json:
            creds_dict = json.loads(creds_json)
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES
            )
        else:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON is not set")

        self._service = build("drive", "v3", credentials=creds)
        self._root_folder_id = settings.google_drive_folder_id

    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        mime_type: str,
        subfolder_name: Optional[str] = None,
    ) -> dict:
        """
        Upload a file to Google Drive.
        Returns dict with 'id' and 'webViewLink'.
        """
        parent_id = self._root_folder_id

        if subfolder_name:
            parent_id = self._get_or_create_folder(subfolder_name, parent_id)

        file_metadata = {
            "name": filename,
            "parents": [parent_id],
        }
        media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype=mime_type, resumable=True)

        file = (
            self._service.files()
            .create(body=file_metadata, media_body=media, fields="id, webViewLink")
            .execute()
        )

        logger.info(f"Uploaded to Drive: {filename} → {file.get('id')}")
        return {"id": file.get("id"), "url": file.get("webViewLink")}

    def download_file(self, file_id: str) -> Tuple[bytes, str]:
        """Download a file from Drive. Returns (content_bytes, mime_type)."""
        metadata = self._service.files().get(fileId=file_id, fields="mimeType").execute()
        mime_type = metadata.get("mimeType", "application/octet-stream")

        request = self._service.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        return buffer.getvalue(), mime_type

    def create_lead_folder(self, lead_id: int, owner_name: str) -> str:
        """Create a dedicated folder for a lead's documents."""
        folder_name = f"Lead_{lead_id}_{owner_name.replace(' ', '_')}"
        return self._get_or_create_folder(folder_name, self._root_folder_id)

    def _get_or_create_folder(self, folder_name: str, parent_id: str) -> str:
        """Get existing folder or create a new one."""
        query = (
            f"name='{folder_name}' and "
            f"'{parent_id}' in parents and "
            f"mimeType='application/vnd.google-apps.folder' and "
            f"trashed=false"
        )
        results = self._service.files().list(q=query, fields="files(id)").execute()
        files = results.get("files", [])

        if files:
            return files[0]["id"]

        metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        folder = self._service.files().create(body=metadata, fields="id").execute()
        return folder["id"]
