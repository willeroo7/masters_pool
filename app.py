from flask import Flask, render_template, jsonify, request
from scraper import MastersScraper
from excel_handler import ExcelHandler
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize handlers
scraper = MastersScraper()
excel_handler = ExcelHandler()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scores', methods=['GET'])
def get_scores():
    try:
        scores = scraper.get_scores()
        response = jsonify({'success': True, 'data': scores})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        error_response = jsonify({'success': False, 'error': str(e)})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    try:
        scores = scraper.get_scores()
        report_path = excel_handler.generate_report(scores)
        return jsonify({
            'success': True,
            'message': 'Report generated successfully',
            'file_path': report_path
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True) 