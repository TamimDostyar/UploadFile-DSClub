# Activate virtual environment | you will need to install python 3.10
if [ ! -d ".venv" ]; then
    python3.10 -m venv .venv
    source .venv/bin/activate
else
    echo "Virtual environment already exists"
    source .venv/bin/activate
fi

python manage.py migrate
python manage.py runserver