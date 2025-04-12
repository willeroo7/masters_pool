import pandas as pd
from scraper import MastersScraper
import unicodedata
from datetime import datetime

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

def get_golfer_statuses():
    """
    Get the status for each golfer from the API.
    Returns a dictionary mapping normalized player names to their status.
    """
    # Initialize scraper and get scores
    scraper = MastersScraper()
    scores_data = scraper.get_scores()
    
    # Create a dictionary to store player statuses
    player_statuses = {}
    if scores_data:
        for player in scores_data:
            name = player['name']
            normalized_name = normalize_name(name)
            status = player['status']
            position = player['position']
            
            # Determine player status
            status_note = ""
            if status == 'C':  # Cut
                status_note = "CUT"
            elif status == 'A' and position == '':  # Active but no position (likely WD)
                status_note = "WD"
            elif status == 'N' and position == '':  # Not active and no position
                status_note = "DNP"
            
            player_statuses[normalized_name] = status_note
    
    return player_statuses

def convert_score_to_int(score):
    """
    Convert a score string to an integer.
    Handles special cases like 'E' (even) and '+' signs.
    """
    if pd.isna(score) or score == '-':
        return 0
    
    if isinstance(score, (int, float)):
        return int(score)
    
    # Handle string scores
    score_str = str(score).strip()
    
    # Handle 'E' for even par
    if score_str == 'E':
        return 0
    
    # Remove '+' sign if present
    if score_str.startswith('+'):
        score_str = score_str[1:]
    
    try:
        return int(score_str)
    except ValueError:
        print(f"Warning: Could not convert score '{score}' to integer")
        return 0

def update_player_totals(scoreboard_df):
    """
    Update the Total column to be the sum of all four rounds.
    """
    # Create a copy of the DataFrame to avoid modifying the original
    updated_df = scoreboard_df.copy()
    
    # Iterate through each row in the DataFrame
    for index, row in updated_df.iterrows():
        # Skip empty rows
        if pd.isna(row['Player']) or row['Player'] == '':
            continue
            
        # Convert each round score to integer
        rd1 = convert_score_to_int(row['Rd1'])
        rd2 = convert_score_to_int(row['Rd2'])
        rd3 = convert_score_to_int(row['Rd3'])
        rd4 = convert_score_to_int(row['Rd4'])
        
        # Calculate total as sum of all four rounds
        total = rd1 + rd2 + rd3 + rd4
        
        # Update the Total column
        updated_df.at[index, 'Total'] = total
    
    return updated_df

def update_cut_player_scores(scoreboard_df, player_statuses):
    """
    Update scores for players who missed the cut (status = 'CUT')
    Set their Rd3 and Rd4 scores to 8
    """
    # Create a copy of the DataFrame to avoid modifying the original
    updated_df = scoreboard_df.copy()
    
    # Count how many players were updated
    updated_count = 0
    
    # Iterate through each row in the DataFrame
    for index, row in updated_df.iterrows():
        # Skip empty rows
        if pd.isna(row['Player']) or row['Player'] == '':
            continue
            
        # Normalize the player name
        normalized_name = normalize_name(row['Player'])
        
        # Check if the player has a CUT status
        if normalized_name in player_statuses and player_statuses[normalized_name] == "CUT":
            # Update Rd3 and Rd4 scores to 8
            updated_df.at[index, 'Rd3'] = 8
            updated_df.at[index, 'Rd4'] = 8
            updated_count += 1
            
            # Recalculate the Total score
            rd1 = convert_score_to_int(row['Rd1'])
            rd2 = convert_score_to_int(row['Rd2'])
            rd3 = 8  # Updated Rd3 score
            rd4 = 8  # Updated Rd4 score
            
            # Calculate new total
            new_total = rd1 + rd2 + rd3 + rd4
            updated_df.at[index, 'Total'] = new_total
    
    print(f"Updated scores for {updated_count} players who missed the cut")
    return updated_df

def calculate_team_scores(scoreboard_df):
    """
    Calculate team scores by taking the 4 best (lowest) scores out of the 6 golfers for each team.
    """
    # Create a copy of the DataFrame to avoid modifying the original
    updated_df = scoreboard_df.copy()
    
    # Get unique team names (excluding empty strings)
    teams = updated_df[updated_df['Team'].notna() & (updated_df['Team'] != '')]['Team'].unique()
    
    # For each team, calculate the score
    for team in teams:
        # Get all rows for this team (including the 6 player rows)
        team_mask = (updated_df['Team'] == team) | ((updated_df['Team'] == '') & (updated_df['Player'] != '') & (updated_df.index > updated_df[updated_df['Team'] == team].index[0]) & (updated_df.index < updated_df[updated_df['Team'] == team].index[0] + 6))
        team_rows = updated_df[team_mask]
        
        # Extract the Total scores for each player
        total_scores = []
        for _, row in team_rows.iterrows():
            if pd.notna(row['Player']) and row['Player'] != '':  # Only include rows with player names
                score = row['Total']  # Total is already an integer
                total_scores.append(score)
        
        # Sort the scores (ascending order - negative scores are better)
        total_scores.sort()  # This puts negative numbers first
        
        # Print debug info
        print(f"\nTeam {team} scores: {total_scores}")
        print(f"Best 4 scores: {total_scores[:4]}")
        
        # Take the 4 best (lowest) scores
        best_scores = total_scores[:4]
        
        # Calculate the team score (sum of the 4 best scores)
        team_score = sum(best_scores)
        print(f"Team score: {team_score}")
        
        # Update the Score column for all rows of this team
        team_indices = updated_df[updated_df['Team'] == team].index
        for idx in team_indices:
            updated_df.at[idx, 'Score'] = team_score
    
    return updated_df

def export_to_excel(df, filename_prefix="masters_pool_scoreboard_with_status"):
    """Export DataFrame to Excel with formatting"""
    # Create Excel writer object
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = f'{filename_prefix}_{timestamp}.xlsx'
    
    # Create a writer object
    writer = pd.ExcelWriter(excel_file, engine='openpyxl')
    
    # Write the DataFrame to Excel
    df.to_excel(writer, sheet_name='Scoreboard', index=False)
    
    # Get the workbook and the worksheet
    workbook = writer.book
    worksheet = writer.sheets['Scoreboard']
    
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

def process_scoreboard():
    """Main function to process the scoreboard data"""
    # Import the team scoreboard
    import team_scoreboard
    
    # Get the scoreboard DataFrame
    scoreboard_df = team_scoreboard.scoreboard_df
    
    # Get golfer statuses
    player_statuses = get_golfer_statuses()
    
    # Display the golfer statuses
    print("\nGolfer Statuses:")
    for name, status in player_statuses.items():
        if status:  # Only show players with a status
            print(f"{name}: {status}")
    
    # Update player totals to be sum of all four rounds
    updated_scoreboard = update_player_totals(scoreboard_df)
    
    # Update scores for players who missed the cut
    updated_scoreboard = update_cut_player_scores(updated_scoreboard, player_statuses)
    
    # Calculate team scores
    final_scoreboard = calculate_team_scores(updated_scoreboard)
    
    # Display the updated scoreboard
    print("\nFinal Scoreboard Structure:")
    print(final_scoreboard.to_string(index=False))
    
    # Export the updated scoreboard to Excel
    export_to_excel(final_scoreboard)
    
    return final_scoreboard

if __name__ == "__main__":
    process_scoreboard() 