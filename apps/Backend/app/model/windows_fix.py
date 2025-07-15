"""
Windows ChromaDB Fix - Must be imported before any ChromaDB imports
"""

import os
import tempfile
from pathlib import Path


def setup_windows_chromadb():
    """Setup environment variables for ChromaDB on Windows"""
    if os.name == "nt":  # Windows
        # Set HOME environment variable if not set
        if not os.environ.get("HOME"):
            home_dir = os.path.expanduser("~")
            os.environ["HOME"] = home_dir

        # Set USERPROFILE if not set
        if not os.environ.get("USERPROFILE"):
            os.environ["USERPROFILE"] = os.path.expanduser("~")

        # Create and set ChromaDB cache directory
        chroma_cache_dir = os.path.join(tempfile.gettempdir(), "chroma_cache")
        os.makedirs(chroma_cache_dir, exist_ok=True)
        os.environ["CHROMA_CACHE_DIR"] = chroma_cache_dir

        # Set additional Windows-specific paths
        if not os.environ.get("LOCALAPPDATA"):
            os.environ["LOCALAPPDATA"] = os.path.join(
                os.path.expanduser("~"), "AppData", "Local"
            )

        if not os.environ.get("APPDATA"):
            os.environ["APPDATA"] = os.path.join(
                os.path.expanduser("~"), "AppData", "Roaming"
            )


# Apply the fix immediately when this module is imported
setup_windows_chromadb()
