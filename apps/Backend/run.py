#!/usr/bin/env python3
"""
Flask application entry point with Windows ChromaDB fix
"""

# Apply Windows fix BEFORE any other imports
import os
import tempfile
import sys
from pathlib import Path


def setup_windows_environment():
    """Setup Windows environment variables and monkey patch pathlib"""
    if os.name == "nt":  # Windows
        # Monkey patch pathlib.Path.home() method
        original_home = Path.home
        
        def patched_home(cls=None):
            """Patched version of Path.home() that works on Windows"""
            try:
                # Try original method first
                return original_home()
            except RuntimeError:
                # Fallback to environment variables or default path
                home_candidates = [
                    os.environ.get('HOME'),
                    os.environ.get('USERPROFILE'),
                    os.path.expanduser('~'),
                    'C:\\Users\\Default'
                ]
                
                for candidate in home_candidates:
                    if candidate and candidate != '~' and os.path.exists(candidate):
                        return Path(candidate)
                
                # Last resort - create a temp directory
                temp_home = os.path.join(tempfile.gettempdir(), 'python_home')
                os.makedirs(temp_home, exist_ok=True)
                return Path(temp_home)
        
        # Apply the monkey patch
        Path.home = classmethod(patched_home)
        
        # Set environment variables as backup
        if not os.environ.get("HOME"):
            try:
                home_dir = os.path.expanduser("~")
                if home_dir == "~":
                    home_dir = os.environ.get("USERPROFILE", "C:\\Users\\Default")
                os.environ["HOME"] = home_dir
            except Exception:
                os.environ["HOME"] = "C:\\Users\\Default"

        # Set USERPROFILE if not set
        if not os.environ.get("USERPROFILE"):
            os.environ["USERPROFILE"] = os.environ.get("HOME", "C:\\Users\\Default")

        # Create and set ChromaDB cache directory
        chroma_cache_dir = os.path.join(tempfile.gettempdir(), "chroma_cache")
        os.makedirs(chroma_cache_dir, exist_ok=True)
        os.environ["CHROMA_CACHE_DIR"] = chroma_cache_dir

        print("✓ Windows environment variables and pathlib patches configured for ChromaDB")


# Apply the fix immediately
setup_windows_environment()

# Verificar que las variables estén configuradas
if os.name == "nt":
    print(f"HOME: {os.environ.get('HOME', 'Not set')}")
    print(f"CHROMA_CACHE_DIR: {os.environ.get('CHROMA_CACHE_DIR', 'Not set')}")
    
    # Test the patched Path.home()
    try:
        test_home = Path.home()
        print(f"✓ Path.home() test successful: {test_home}")
    except Exception as e:
        print(f"❌ Path.home() test failed: {e}")

# Now safe to import Flask app
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
