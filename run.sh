# Activate virtual environment | you will need to install python 3.10
if [ ! -d ".venv" ]; then
    python3.10 -m venv .venv
    source .venv/bin/activate
else
    echo "Virtual environment already exists"
    source .venv/bin/activate
fi

# Suppress TensorFlow warnings and optimize for low-memory environment
export TF_CPP_MIN_LOG_LEVEL=3
export TF_ENABLE_ONEDNN_OPTS=0
export CUDA_VISIBLE_DEVICES=-1
export TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_MEMORY_ALLOCATION=0.2

python manage.py migrate
# Use SSL for the development server
python manage.py runserver_plus 0.0.0.0:8000 --cert-file=ssl/cert.pem --key-file=ssl/key.pem