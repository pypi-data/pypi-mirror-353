from google.cloud import storage
from typing import Optional, Tuple, Dict, Any
import os

class GCSClient:
    def __init__(self, credentials_path: Optional[str] = None, project_id: Optional[str] = None):
        """
        Initialize GCS client with credentials
        
        Args:
            credentials_path: Path to service account JSON file
            project_id: GCP project ID
        """
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        self.storage_client = storage.Client(project=project_id)
    
    def upload_to_gcs(self, bucket_name: str, file_name: str, file_data: bytes, 
                     meta_data: Optional[Dict[str, Any]] = None,
                     content_type: str = 'application/pdf') -> Tuple[bool, Optional[str]]:
        """
        Upload data to Google Cloud Storage
        
        Args:
            bucket_name: GCS bucket name
            file_name: Name for the file in GCS
            file_data: File data as bytes
            meta_data: Optional metadata dictionary
            content_type: MIME type of the file
            
        Returns:
            Tuple of (success: bool, gcs_uri: str or None)
        """
        try:
            gcs_uri = f"gs://{bucket_name}/{file_name}"
            
            # Get the bucket
            bucket = self.storage_client.bucket(bucket_name)
            
            # Create a blob (object) in the bucket
            blob = bucket.blob(file_name)
            
            # Set metadata if provided
            if meta_data:
                blob.metadata = meta_data
            
            # Upload the bytes directly
            blob.upload_from_string(file_data, content_type=content_type)
            
            print(f'GCS URI: {gcs_uri}')
            
            return True, gcs_uri
            
        except Exception as e:
            print(f'Upload failed: {e}')
            return False, None