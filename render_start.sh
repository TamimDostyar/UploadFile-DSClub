#!/bin/bash
set -e  # Exit immediately if a command fails

echo "Setting up environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Ensure ML dependencies are installed
echo "Installing ML-specific dependencies..."
pip install huggingface-hub transformers torch --no-cache-dir

# Print diagnostic information
echo "=== Environment Information ==="
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Installed packages:"
pip list
echo "=========================="

# Apply database migrations
echo "Applying migrations..."
python3 manage.py migrate

# Explicitly download the model
echo "Downloading ML model..."
# Create a Python script for downloading model
cat > download_model_script.py << 'EOF'
import os
import sys
from upload.Notebook.download_model import download_model

# Print environment information
print("=== Model Download Environment ===")
print(f"Working directory: {os.getcwd()}")
print(f"HF_TOKEN environment variable set: {'Yes' if 'HF_TOKEN' in os.environ else 'No'}")
print("================================")

try:
    print("Attempting to download model...")
    model_path = download_model()
    print(f"Model downloaded successfully to: {model_path}")
    sys.exit(0)
except Exception as e:
    print(f"Error downloading model: {str(e)}")
    sys.exit(1)
EOF

# Run the model download script
python download_model_script.py

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Start Gunicorn process for production
echo "Starting Gunicorn server..."
gunicorn fileupload.wsgi:application --bind 0.0.0.0:$PORT --log-level debug 