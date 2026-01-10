import os
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional
import logging


logger = logging.getLogger(__name__)


@dataclass
class LoadedJSON:
    json_data: Any
    meta_data: Dict[str, Any]
    data_path: str
    meta_path: str


def load_json_data(bronze_path: str, meta_path: str) -> LoadedJSON:
    """
    Load the latest JSON and its matching .meta.json file
    from the bronze layer.

    Parameters
    ----------
    bronze_path : str
        Path to directory containing raw JSON files.
    meta_path : str
        Path to directory containing metadata JSON files.

    Returns
    -------
    LoadedJSON
        Struct containing json_data, meta_data, and paths.
    """

    if not os.path.isdir(bronze_path):
        raise FileNotFoundError(f"Bronze directory does not exist: {bronze_path}")

    if not os.path.isdir(meta_path):
        raise FileNotFoundError(f"Metadata directory does not exist: {meta_path}")

    files = [f for f in os.listdir(bronze_path) if f.endswith(".json")]
    if not files:
        raise FileNotFoundError("No JSON files found in bronze directory.")

    latest_file = sorted(files)[-1]
    meta_file = latest_file.replace(".json", ".meta.json")

    data_file_path = os.path.join(bronze_path, latest_file)
    meta_file_path = os.path.join(meta_path, meta_file)

    if not os.path.exists(meta_file_path):
        raise FileNotFoundError(f"Matching metadata file not found: {meta_file_path}")

    logger.info(f"Loading data file: {data_file_path}")
    logger.info(f"Loading metadata file: {meta_file_path}")

    # Load main data
    with open(data_file_path, "r") as f:
        json_data = json.load(f)

    # Load metadata
    with open(meta_file_path, "r") as f:
        meta_data = json.load(f)

  
    return LoadedJSON(
        json_data=json_data,
        meta_data=meta_data,
        data_path=data_file_path,
        meta_path=meta_file_path,
    )
