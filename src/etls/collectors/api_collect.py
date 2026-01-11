import os
import json
import uuid
import logging
from datetime import datetime, timezone
import requests
from requests.auth import HTTPBasicAuth
from typing import Optional, Dict, Tuple, Union


class APIClient:
    def __init__(
                self, 
                timeout: int = 30,
                max_attempts: int = 3,
                storage_path: Optional[str] = None,
                headers: Optional[Dict[str, str]] = None,
                auth: Optional[Union[Tuple[str, str], None]] = None
    ):
        """
        API Client to fetch JSON data with optional authentication.

        Args:
            storage_path (str): Folder to store data (defaults to data_storage/bronze).
            timeout (int): Request timeout in seconds.
            max_attempts (int): Number of retries for failed requests.
            headers (dict, optional): HTTP headers to include in the request.
                For example: {"Authorization": "Bearer <TOKEN>"}
            auth (tuple, optional): Basic auth credentials as (username, password)
        """
        # Set defaults
        # Default folder: data_storage/bronze
        if storage_path is None:
            storage_path = 'data_storage/bronze/'
            logging.info(f'storage path is for test {storage_path}')
        

        self.storage_path = os.path.abspath(storage_path)
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.headers = headers or {}
        self.auth = HTTPBasicAuth(*auth) if auth else None

   
    # Utility Methods
    def _save_json(self, data: dict, path: str):
        try:
            # Ensure the folder exists
            folder = os.path.dirname(path)
            os.makedirs(folder, exist_ok=True)

            logging.info('Saving the json file....')
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"[SAVED]: {path}")

        except Exception as e:
            logging.info(f'[ERROR]: {e}')



    def _timestamp(self):
        return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")


  
    # Main API Fetch Method
    def fetch(self, api_url: str):
        """Fetch JSON from API and store both data and metadata."""

        ts = self._timestamp()
        uid = uuid.uuid4().hex[:8]

        data_filename = f"{uid}__{ts}.json"
        meta_filename = f"{uid}__{ts}.meta.json"

        data_path = os.path.join(self.storage_path, data_filename)
        meta_path = os.path.join(self.storage_path+'/meta_data/', meta_filename)

        metadata = {
            "api_url": api_url,
            "req_time": ts,
            "filename": data_filename,
            "status": None,
            "http_status": None,
            "attempts": 0,
            "error": None,
        }

        # Fetch Loop
        for attempt in range(1, self.max_attempts + 1):
            try:
                logging.info(f"Fetching {api_url} (attempt {attempt})")

                response = requests.get(
                        api_url, 
                        timeout=self.timeout,
                        headers=self.headers,
                        auth=self.auth
                        )
                
                response.raise_for_status()

                request_data = response.json()

                # Save data
                #logging.info('Saving the api data in bronze')
                #self._save_json(request_data, data_path)

                # Metadata success
                metadata["status"] = "success"
                metadata["http_status"] = response.status_code
                metadata["attempts"] = attempt

                break  # stop retries

            except Exception as e:
                logging.warning(f"Attempt {attempt} failed: {e}")
                metadata["error"] = str(e)

                if attempt == self.max_attempts:
                    metadata["status"] = "failed"
                    metadata["http_status"] = getattr(getattr(e, "response", None), "status_code", None)
                    metadata["attempts"] = attempt


        # Save metadata
        #logging.info('Saving the meta data..')
        #self._save_json(metadata, meta_path)

        return {
            "data_path": data_path,
            "meta_path": meta_path,
            "metadata": metadata,
            "req_data": request_data,
            "status":metadata["status"]
        }
