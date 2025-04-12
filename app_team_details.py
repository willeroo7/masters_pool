from flask import Flask, render_template, jsonify, request
from scraper import MastersScraper
from excel_handler import ExcelHandler
import os
from datetime import datetime
import pandas as pd
from cleanup_scoreboard import process_scoreboard
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize handlers
scraper = MastersScraper()
excel_handler = ExcelHandler()

# Cache for processed scoreboard
_cached_scoreboard = None
_last_update_time = None

def get_cached_scoreboard():
    global _cached_scoreboard, _last_update_time
    current_time = datetime.now()
    
    # Update cache if it's None or older than 5 minutes
    if _cached_scoreboard is None or _last_update_time is None or \
       (current_time - _last_update_time).total_seconds() > 300:
        logger.info("Updating scoreboard cache...")
        _cached_scoreboard = process_scoreboard()
        _last_update_time = current_time
    
    return _cached_scoreboard

@app.route('/')
def index():
    return render_template('index_team_details.html')

@app.route('/api/team-scores', methods=['GET'])
def get_team_scores():
    try:
        logger.debug("Getting team scores...")
        
        # Get the cached scoreboard
        final_scoreboard = get_cached_scoreboard()
        
        # Sort by Score (ascending order since negative is better)
        def score_to_float(score):
            if pd.isna(score) or score == '' or isinstance(score, str):
                return float('inf')
            return float(score)
        
        final_scoreboard = final_scoreboard.sort_values(
            by='Score',
            key=lambda x: x.map(score_to_float)
        )
        
        # Convert DataFrame to nested team/player structure
        result = []
        current_rank = 1
        
        # Get unique teams
        teams = final_scoreboard[final_scoreboard['Team'].notna() & (final_scoreboard['Team'] != '')]['Team'].unique()
        
        for team_name in teams:
            # Get team row
            team_row = final_scoreboard[final_scoreboard['Team'] == team_name].iloc[0]
            
            # Get player rows for this team
            team_mask = (
                (final_scoreboard['Team'] == team_name) |  # Team row
                (  # Player rows: empty team name and between this team and next team
                    (final_scoreboard['Team'] == '') & 
                    (final_scoreboard.index > final_scoreboard[final_scoreboard['Team'] == team_name].index[0]) &
                    (final_scoreboard.index < final_scoreboard[final_scoreboard['Team'] == team_name].index[0] + 7)
                )
            )
            team_rows = final_scoreboard[team_mask]
            
            # Create team dict
            team_dict = {
                'rank': current_rank,
                'team': team_name,
                'score': int(team_row['Score']) if pd.notna(team_row['Score']) else None,
                'players': []
            }
            
            # Add players
            for _, player_row in team_rows.iterrows():
                if pd.notna(player_row['Player']) and player_row['Player'] != '':
                    player_dict = {
                        'name': player_row['Player'],
                        'tier': int(player_row['Tier']),
                        'rounds': [
                            int(player_row['Rd1']) if pd.notna(player_row['Rd1']) else None,
                            int(player_row['Rd2']) if pd.notna(player_row['Rd2']) else None,
                            int(player_row['Rd3']) if pd.notna(player_row['Rd3']) else None,
                            int(player_row['Rd4']) if pd.notna(player_row['Rd4']) else None
                        ],
                        'total': int(player_row['Total']) if pd.notna(player_row['Total']) else None
                    }
                    team_dict['players'].append(player_dict)
            
            result.append(team_dict)
            current_rank += 1
        
        response = jsonify({'success': True, 'data': result})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    except Exception as e:
        logger.error(f"Error in get_team_scores: {str(e)}", exc_info=True)
        error_response = jsonify({'success': False, 'error': str(e)})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

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
    
    # Run on port 5001 instead of the default 5000
    app.run(debug=True, port=5001) 