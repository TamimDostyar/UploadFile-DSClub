# Team Shark - ML Image Processing Platform
Created by: Tamim Dostyar


### Prerequisites
- Python < 3.10
- pip

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/tamimdostyar/UploadFile-DSClub.git
   cd DS-Club
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

5. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Try it out: http://localhost:8000 in your browser

## Project Structure
```
UploadFile-DSClub/
├── fileupload/          # Project settings
├── upload/             # Main application
│   ├── templates/     # HTML templates
│   ├── models.py      # Database models
│   ├── views.py       # View logic
│   ├── forms.py       # Form definitions
│   └── ml_processor.py # ML processing logic
├── media/             # Uploaded files
└── manage.py          # Django management script
```

## Acknowledgments
# Got below files from Google and modified them to fit the project
- Ocean background: Unsplash - https://unsplash.com/photos/ocean-background
- Shark animation: PNG All - https://www.pngall.com/shark-png