"""
Central configuration utilities for paths and environment-driven settings.
"""

import os
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parent


def get_storage_dir() -> str:
    """
    Resolve the storage directory using the STORAGE_DIR environment variable,
    defaulting to <project_root>/storage.
    Ensures the directory exists.
    """
    storage_dir = os.getenv("STORAGE_DIR")
    if not storage_dir:
        storage_dir = str(get_project_root() / "storage")
    os.makedirs(storage_dir, exist_ok=True)
    return storage_dir


def get_tmp_dir() -> str:
    """
    Resolve the tmp directory using TMP_DIR environment variable,
    defaulting to <project_root>/tmp.
    Ensures the directory exists.
    """
    tmp_dir = os.getenv("TMP_DIR")
    if not tmp_dir:
        tmp_dir = str(get_project_root() / "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    return tmp_dir


