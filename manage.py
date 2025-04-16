#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Made by Tamim Dostyar
"""Django's command-line utility for administrative tasks."""
import os
import sys

def download_corn_model():
    """Tries to download the model but continues if it fails."""
    try:
        # First check if the required modules are installed
        try:
            import huggingface_hub
            import tensorflow
        except ImportError as e:
            print(f"WARNING: ML dependencies missing ({str(e)}). Continuing without ML features.")
            return
            
        from upload.Notebook.download_model import download_model
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, "upload", "Notebook", "corn_model_1.keras")
        if not os.path.exists(MODEL_PATH):
            print("Attempting to download corn disease model...")
            result = download_model()
            if result:
                print(f"Model setup complete: {result}")
            else:
                print("WARNING: Model download failed, but will continue with startup")
    except Exception as e:
        print(f"Error during model setup: {str(e)}")
        print("WARNING: Will continue with startup without the model")

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fileupload.settings')
    
    # Try to download the model but don't stop if it fails
    try:
        download_corn_model()
    except Exception as e:
        print(f"Model setup failed but continuing: {str(e)}")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()