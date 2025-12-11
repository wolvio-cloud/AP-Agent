from google.cloud import storage
from fastapi import UploadFile, HTTPException, status
from typing import Optional
import os
import uuid
from datetime import timedelta
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Allowed file types and their extensions
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/jpg',
    'image/png'
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes


class StorageService:
    """Service for managing document storage in Google Cloud Storage"""

    def __init__(self):
        """Initialize GCS client"""
        try:
            # For local development, you can use a mock or skip GCS
            if settings.ENVIRONMENT == "development" and not settings.GOOGLE_APPLICATION_CREDENTIALS:
                logger.warning("GCS credentials not configured. Using local storage fallback.")
                self.client = None
                self.bucket = None
                self.use_local = True
                # Create local storage directory
                os.makedirs("./storage/invoices", exist_ok=True)
            else:
                self.client = storage.Client()
                self.bucket = self.client.bucket(settings.GCS_BUCKET_NAME)
                self.use_local = False
                logger.info(f"Connected to GCS bucket: {settings.GCS_BUCKET_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize storage client: {str(e)}")
            # Fallback to local storage
            self.client = None
            self.bucket = None
            self.use_local = True
            os.makedirs("./storage/invoices", exist_ok=True)

    def _validate_file(self, file: UploadFile) -> None:
        """
        Validate file type and size

        Args:
            file: UploadFile object

        Raises:
            HTTPException: If file is invalid
        """
        # Check file extension
        filename = file.filename or ""
        extension = os.path.splitext(filename)[1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Check MIME type
        if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Supported MIME types: {', '.join(ALLOWED_MIME_TYPES)}"
            )

    async def upload_document(self, file: UploadFile, organization_id: str) -> tuple[str, str]:
        """
        Upload document to GCS or local storage

        Args:
            file: UploadFile object
            organization_id: Organization UUID

        Returns:
            Tuple of (file_path, file_type)

        Raises:
            HTTPException: If upload fails
        """
        try:
            # Validate file
            self._validate_file(file)

            # Read file content
            content = await file.read()

            # Check file size
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB"
                )

            # Generate unique filename
            file_extension = os.path.splitext(file.filename or "")[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = f"{organization_id}/{unique_filename}"

            if self.use_local:
                # Local storage fallback
                local_path = f"./storage/invoices/{file_path}"
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                with open(local_path, "wb") as f:
                    f.write(content)

                logger.info(f"Uploaded file to local storage: {local_path}")
                storage_path = f"local://{file_path}"
            else:
                # Upload to GCS
                blob = self.bucket.blob(file_path)
                blob.upload_from_string(content, content_type=file.content_type)

                logger.info(f"Uploaded file to GCS: gs://{settings.GCS_BUCKET_NAME}/{file_path}")
                storage_path = f"gs://{settings.GCS_BUCKET_NAME}/{file_path}"

            # Determine file type
            file_type = file_extension.lstrip('.')

            return storage_path, file_type

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to upload document: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload document: {str(e)}"
            )

    def download_document(self, file_path: str) -> bytes:
        """
        Download document from GCS or local storage

        Args:
            file_path: GCS path (gs://bucket/path or local://path)

        Returns:
            File content as bytes

        Raises:
            HTTPException: If download fails
        """
        try:
            if file_path.startswith("local://"):
                # Local storage
                local_path = file_path.replace("local://", "./storage/invoices/")
                with open(local_path, "rb") as f:
                    return f.read()
            else:
                # GCS storage
                blob_path = file_path.replace(f"gs://{settings.GCS_BUCKET_NAME}/", "")
                blob = self.bucket.blob(blob_path)
                return blob.download_as_bytes()

        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        except Exception as e:
            logger.error(f"Failed to download document: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to download document"
            )

    def delete_document(self, file_path: str) -> bool:
        """
        Delete document from GCS or local storage

        Args:
            file_path: GCS path (gs://bucket/path or local://path)

        Returns:
            True if successful

        Raises:
            HTTPException: If deletion fails
        """
        try:
            if file_path.startswith("local://"):
                # Local storage
                local_path = file_path.replace("local://", "./storage/invoices/")
                if os.path.exists(local_path):
                    os.remove(local_path)
                    logger.info(f"Deleted file from local storage: {local_path}")
            else:
                # GCS storage
                blob_path = file_path.replace(f"gs://{settings.GCS_BUCKET_NAME}/", "")
                blob = self.bucket.blob(blob_path)
                blob.delete()
                logger.info(f"Deleted file from GCS: {file_path}")

            return True

        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document"
            )

    def get_signed_url(self, file_path: str, expiry_minutes: int = 60) -> str:
        """
        Generate signed URL for secure file access

        Args:
            file_path: GCS path
            expiry_minutes: URL expiry time in minutes

        Returns:
            Signed URL string

        Raises:
            HTTPException: If generation fails
        """
        try:
            if file_path.startswith("local://"):
                # For local storage, return a local file path
                # In production with proper backend, this would be a proper endpoint
                return f"/api/v1/invoices/download?path={file_path}"

            # GCS signed URL
            blob_path = file_path.replace(f"gs://{settings.GCS_BUCKET_NAME}/", "")
            blob = self.bucket.blob(blob_path)

            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=expiry_minutes),
                method="GET"
            )

            return url

        except Exception as e:
            logger.error(f"Failed to generate signed URL: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate signed URL"
            )


# Singleton instance
storage_service = StorageService()
