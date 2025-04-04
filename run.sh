#!/bin/bash
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install setuptools wheel

echo "Installing dependencies..."
pip install Django asgiref sqlparse django-crispy-forms crispy-bootstrap5 djangorestframework
pip install python-dotenv dotenv numpy pandas openpyxl xlrd xlsx2csv Pillow geopy requests

pip install tensorflow torch huggingface-hub transformers || echo "Warning: Some ML packages couldn't be installed, but we'll continue with basic Django setup."

pip install -r requirements.txt || echo "Some packages couldn't be installed."

python -c "from PIL import Image" || { echo "Critical dependency Pillow is missing. Installing again..."; pip install Pillow; }

python -c "import geopy" || { echo "Critical dependency geopy is missing. Installing again..."; pip install geopy; }

python -c "import requests" || { echo "Critical dependency requests is missing. Installing again..."; pip install requests; }

python3 manage.py migrate
python3 manage.py runserver