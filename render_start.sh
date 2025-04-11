#!/bin/bash

# Don't recreate venv if it exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir

# Ensure ML dependencies are installed but with a timeout
echo "Installing ML-specific dependencies..."
timeout 300 pip install huggingface-hub transformers --no-cache-dir || echo "Warning: ML dependency installation timed out, continuing anyway"
timeout 300 pip install torch --no-cache-dir || echo "Warning: PyTorch installation timed out, continuing anyway"

# Print diagnostic information (basic only)
echo "=== Environment Information ==="
python --version
echo "=========================="

# Apply database migrations
echo "Applying migrations..."
python3 manage.py migrate

# Check if model already exists before trying to download
MODEL_PATH="upload/Notebook/corn_model_1.keras"
if [ -f "$MODEL_PATH" ]; then
    echo "Model file already exists, skipping download"
else
    # Explicitly download the model with a timeout
    echo "Downloading ML model..."
    timeout 300 python -c "from upload.Notebook.download_model import download_model; download_model()" || echo "Warning: Model download timed out, continuing anyway"
fi

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Start Gunicorn process for production
echo "Starting Gunicorn server..."
gunicorn fileupload.wsgi:application --bind 0.0.0.0:$PORT --log-level info --timeout 120 