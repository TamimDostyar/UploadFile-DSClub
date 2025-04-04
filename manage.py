#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Made by Tamim Dostyar
"""Django's command-line utility for administrative tasks."""
import os
import sys
try:
    from upload.Notebook.download_model import download_model
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "Notebook", "corn_model_1.keras")
    if not os.path.exists(MODEL_PATH):
        download_model()
except Exception as e:
    print(f"Error downloading model: {str(e)}")
    raise

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fileupload.settings')
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
