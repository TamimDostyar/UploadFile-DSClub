#!/bin/bash
# This script sets up only basic Django without machine learning components

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Update pip and install basic tools
pip install --upgrade pip
pip install setuptools wheel

# Install only the essential Django packages
echo "Installing Django and basic dependencies..."
pip install Django==5.0.2 asgiref==3.8.1 sqlparse==0.5.3
pip install django-crispy-forms==2.1 crispy-bootstrap5==2024.2 djangorestframework==3.16.0
pip install python-dotenv==1.1.0 Pillow==10.2.0 

echo "Setting up database..."
python3 manage.py migrate

echo "Starting server..."
python3 manage.py runserver 