#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import os
import sys


def test_basic_imports():
    """Test basic Python imports"""
    try:
        import json
        import re
        import tempfile
        from pathlib import Path

        print("✓ Basic Python imports work")
        return True
    except ImportError as e:
        print(f"✗ Basic imports failed: {e}")
        return False


def test_flask_imports():
    """Test Flask related imports"""
    try:
        import flask
        from flask_cors import CORS

        print("✓ Flask imports work")
        return True
    except ImportError as e:
        print(f"✗ Flask imports failed: {e}")
        return False


def test_langchain_imports():
    """Test LangChain imports"""
    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain.chains import create_retrieval_chain
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_ollama import OllamaLLM

        print("✓ LangChain imports work")
        return True
    except ImportError as e:
        print(f"✗ LangChain imports failed: {e}")
        return False


def test_chromadb_imports():
    """Test ChromaDB imports with Windows fix"""
    try:
        import tempfile

        # Apply Windows fix
        if os.name == "nt":  # Windows
            if not os.environ.get("USERPROFILE"):
                os.environ["USERPROFILE"] = os.path.expanduser("~")
            chroma_cache_dir = os.path.join(tempfile.gettempdir(), "chroma_cache")
            os.makedirs(chroma_cache_dir, exist_ok=True)
            os.environ["CHROMA_CACHE_DIR"] = chroma_cache_dir

        from langchain_chroma import Chroma
        import chromadb

        print("✓ ChromaDB imports work")
        return True
    except ImportError as e:
        print(f"✗ ChromaDB imports failed: {e}")
        return False


def test_transformers_imports():
    """Test Transformers imports"""
    try:
        from transformers import pipeline, T5Tokenizer, T5ForConditionalGeneration

        print("✓ Transformers imports work")
        return True
    except ImportError as e:
        print(f"✗ Transformers imports failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Testing imports for Medical Flashcard Backend...")
    print("=" * 50)

    tests = [
        test_basic_imports,
        test_flask_imports,
        test_transformers_imports,
        test_chromadb_imports,
        test_langchain_imports,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✓ All imports successful! Backend should work.")
        return True
    else:
        print("✗ Some imports failed. Check missing dependencies.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
