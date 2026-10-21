"""Variables de entorno que ChromaDB necesita en Windows. Llamar antes de importar chromadb."""

import os
import tempfile


def setup_windows_environment():
    if os.name != "nt":
        return
    home = os.environ.get("USERPROFILE") or os.environ.get("HOME") or os.path.expanduser("~")
    if not home or home == "~":
        home = os.path.join(tempfile.gettempdir(), "python_home")
        os.makedirs(home, exist_ok=True)
    os.environ.setdefault("HOME", home)
    os.environ.setdefault("USERPROFILE", home)
    os.environ.setdefault("LOCALAPPDATA", os.path.join(home, "AppData", "Local"))
    os.environ.setdefault("APPDATA", os.path.join(home, "AppData", "Roaming"))

    chroma_cache_dir = os.path.join(tempfile.gettempdir(), "chroma_cache")
    os.makedirs(chroma_cache_dir, exist_ok=True)
    os.environ.setdefault("CHROMA_CACHE_DIR", chroma_cache_dir)
