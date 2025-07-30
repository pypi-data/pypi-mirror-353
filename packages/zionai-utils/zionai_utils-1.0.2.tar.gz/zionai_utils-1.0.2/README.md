# GCS Utils

A simple utility library for Google Cloud Storage operations.

## Installation

```bash
pip install zionai_utils==1.0.2
```

## Usage

```python
from zionai_utils import GCSClient

# Initialize with service account key
client = GCSClient(
    credentials_path="/path/to/service-account.json",
    project_id="your-project-id"
)

# Upload file
success, gcs_uri = client.upload_to_gcs(
    bucket_name="your-bucket",
    file_name="document.pdf",
    file_data=file_bytes,
    meta_data={"author": "John Doe"}
)
```