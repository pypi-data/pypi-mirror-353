import requests
import json
import time
import base64
import os
import mimetypes
from typing import Dict, Union, Optional, Type
from pydantic import BaseModel


class VisionClient:
    def __init__(self, token: str, base_url: str = "https://api.regia.cloud/v1"):
        self.token = token
        self.base_url = base_url.rstrip("/")

    def extract(
        self,
        file: Union[str, bytes],
        schema: Union[Dict, Type[BaseModel]],
        filename: str = "document.pdf",
        mime_type: Optional[str] = None
    ) -> Dict:
        """
        Submits a file and schema to the extractor API.
        file: str (file path or base64) or bytes
        schema: dict or Pydantic model
        filename: str - filename for the uploaded file
        mime_type: Optional[str] - mime type, will be auto-detected if not provided
        """
        # Process schema
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            schema_payload = self._pydantic_to_extraction_schema(schema)
        elif isinstance(schema, dict):
            schema_payload = schema
        else:
            raise ValueError(
                "Schema must be a dict or a Pydantic BaseModel class.")

        # Read file content and determine mime type
        if isinstance(file, str):
            if os.path.exists(file):
                with open(file, "rb") as f:
                    file_bytes = f.read()
                # Auto-detect mime type from file path if not provided
                if mime_type is None:
                    detected_type, _ = mimetypes.guess_type(file)
                    mime_type = detected_type or "application/octet-stream"
                # Update filename to match the actual file
                if filename == "document.pdf":
                    filename = os.path.basename(file)
            else:
                try:
                    file_bytes = base64.b64decode(file)
                except Exception:
                    raise ValueError("Invalid file path or base64 string.")
                # For base64 strings, use provided mime_type or default
                if mime_type is None:
                    mime_type = "application/octet-stream"
        elif isinstance(file, bytes):
            file_bytes = file
            # For bytes, use provided mime_type or default
            if mime_type is None:
                mime_type = "application/octet-stream"
        else:
            raise ValueError(
                "File must be a valid path, bytes, or base64 string.")

        # Auto-detect mime type from filename if still not determined
        if mime_type is None or mime_type == "application/octet-stream":
            detected_type, _ = mimetypes.guess_type(filename)
            if detected_type:
                mime_type = detected_type

        files = {
            "pdf_file": (filename, file_bytes, mime_type),
            "schema": ("schema.json", json.dumps(schema_payload), "application/json")
        }

        response = requests.post(
            f"{self.base_url}/vision/extract",
            files=files,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        response.raise_for_status()
        return response.json()

    def _pydantic_to_extraction_schema(self, model: Type[BaseModel]) -> dict:
        """
        Converts a Pydantic model to JSON Schema
        """
        return model.model_json_schema()

