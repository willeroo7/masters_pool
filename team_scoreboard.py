import pandas as pd
import os
from participants_teams import extract_teams_data
from scraper import MastersScraper
from datetime import datetime
import unicodedata

def normalize_name(name):
    """Normalize player names for consistent matching"""
    # Convert to lowercase
    name = name.lower()
    # Special case for Nicolai Højgaard
    name = name.replace('ø', 'o')
    # Remove accents/diacritics
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    # Remove extra spaces around dots (e.g., "J. T." -> "J.T.")
    name = name.replace(' . ', '.').replace('. ', '.').replace(' .', '.')
    return name

# Initialize scraper and get scores
scraper = MastersScraper()
scores_data = scraper.get_scores()

# Create a dictionary to store player scores
player_scores = {}
if scores_data:
    for player in scores_data:
        name = player['name']
        normalized_name = normalize_name(name)
        rounds = player['rounds']
        # Get relative to par scores for all rounds regardless of status
        player_scores[normalized_name] = {
            'Rd1': rounds['round1']['relative_to_par'],
            'Rd2': rounds['round2']['relative_to_par'],
            'Rd3': rounds['round3']['relative_to_par'],
            'Rd4': rounds['round4']['relative_to_par'],
            'Total': player['total_score']
        }

# Get teams data
teams_df = extract_teams_data()
if teams_df is None:
    print("Error: Could not load teams data")
    exit(1)

# Debug: Print players missing from API data
print("\nPlayers missing from API data:")
for _, team in teams_df.iterrows():
    for tier in range(1, 7):
        player_name = team[f'Tier {tier}']
        normalized_name = normalize_name(player_name)
        if normalized_name not in player_scores:
            print(f"  {player_name} (Tier {tier}) - Normalized: {normalized_name}")
print()

# Create empty list to store rows
scoreboard_rows = []

# For each team, create 6 rows (one for each tier) plus a blank row
for _, team in teams_df.iterrows():
    # First row gets the team name and first player
    player_name = team['Tier 1']
    normalized_name = normalize_name(player_name)
    player_data = player_scores.get(normalized_name, {'Rd1': '-', 'Rd2': '-', 'Rd3': '-', 'Rd4': '-', 'Total': '-'})
    scoreboard_rows.append({
        'Team': team['Name'],
        'Score': 'scoretbd',
        'Tie Breaker': team['Tie Breaker'],
        'Player': player_name,
        'Tier': 1,
        'Rd1': player_data['Rd1'],
        'Rd2': player_data['Rd2'],
        'Rd3': player_data['Rd3'],
        'Rd4': player_data['Rd4'],
        'Total': player_data['Total']
    })
    # Next 5 rows are blank for team info but contain players
    for tier in range(2, 7):  # Tiers 2-6
        player_name = team[f'Tier {tier}']
        normalized_name = normalize_name(player_name)
        player_data = player_scores.get(normalized_name, {'Rd1': '-', 'Rd2': '-', 'Rd3': '-', 'Rd4': '-', 'Total': '-'})
        scoreboard_rows.append({
            'Team': '',
            'Score': '',
            'Tie Breaker': '',
            'Player': player_name,
            'Tier': tier,
            'Rd1': player_data['Rd1'],
            'Rd2': player_data['Rd2'],
            'Rd3': player_data['Rd3'],
            'Rd4': player_data['Rd4'],
            'Total': player_data['Total']
        })
    # Add a blank row after each team
    scoreboard_rows.append({
        'Team': '',
        'Score': '',
        'Tie Breaker': '',
        'Player': '',
        'Tier': '',
        'Rd1': '',
        'Rd2': '',
        'Rd3': '',
        'Rd4': '',
        'Total': ''
    })

# Create scoreboard DataFrame
scoreboard_df = pd.DataFrame(scoreboard_rows)

# Set display options for better readability
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

# Set column order
column_order = ['Team', 'Score', 'Tie Breaker', 'Player', 'Tier', 'Rd1', 'Rd2', 'Rd3', 'Rd4', 'Total']
scoreboard_df = scoreboard_df[column_order]

# Display the result
print("\nScoreboard Structure:")
print(scoreboard_df.to_string(index=False))

'''
# Export to Excel with formatting
def export_to_excel(df):
    # Create Excel writer object
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = f'masters_pool_scoreboard_{timestamp}.xlsx'
    
    # Create a writer object
    writer = pd.ExcelWriter(excel_file, engine='openpyxl')
    
    # Write the DataFrame to Excel
    df.to_excel(writer, sheet_name='Scoreboard', index=False)
    
    # Get the workbook and the worksheet
    workbook = writer.book
    worksheet = writer.sheets['Scoreboard']
    
    # Define formats
    # Auto-adjust column widths
    for column in worksheet.columns:
        max_length = 0
        column = [cell for cell in column]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
    
    # Save the Excel file
    writer.close()
    print(f"\nExcel file created: {excel_file}")
    return excel_file

# Export the scoreboard to Excel
excel_file = export_to_excel(scoreboard_df)
'''