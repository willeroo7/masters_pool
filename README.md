# Masters Golf Tournament Score Tracker

A web-based application that scrapes and displays Masters Golf Tournament scores, with Excel report generation capabilities.

## Features
- Web scraping of Masters Tournament scores
- Excel report generation
- Web-based dashboard for score visualization
- Data export capabilities

## Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Project Structure
- `app.py`: Main Flask application
- `scraper.py`: Web scraping functionality
- `excel_handler.py`: Excel file operations
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and other static files
- `data/`: Generated Excel files and data storage 