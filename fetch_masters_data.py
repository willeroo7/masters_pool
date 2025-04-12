import requests
import json
from datetime import datetime
import pandas as pd
import os

def fetch_masters_data(year=2025):
    """
    Fetch the Masters Tournament data for a specific year.
    
    Args:
        year (int): The year of the Masters Tournament (default: 2025)
        
    Returns:
        dict: The JSON data from the Masters Tournament API
    """
    url = f"https://www.masters.com/en_US/scores/feeds/{year}/scores.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.masters.com/'
    }
    
    print(f"Fetching Masters Tournament data for {year}...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        print(f"API Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        data = response.json()
        return data
        
    except requests.RequestException as e:
        print(f"Error fetching data: {str(e)}")
        print(f"Response content: {response.text if 'response' in locals() else 'No response'}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

def save_data_to_file(data, year=2025):
    """
    Save the JSON data to a file.
    
    Args:
        data (dict): The JSON data to save
        year (int): The year of the Masters Tournament
    """
    if data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"masters_data_{year}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Data saved to {filename}")
    else:
        print("No data to save")

def display_player_data(data):
    """
    Display player data from the JSON response.
    
    Args:
        data (dict): The JSON data from the Masters Tournament API
    """
    if not data:
        print("No data available")
        return
    
    # The player data is in data.data.player
    players = data.get('data', {}).get('player', [])
    print(f"\nFound {len(players)} players in the data")
    
    if not players:
        print("No player data found")
        return
    
    print("\nPlayer Data:")
    print("-" * 80)
    print(f"{'Name':<30} {'Position':<10} {'Total':<10} {'To Par':<10} {'Status':<10}")
    print("-" * 80)
    
    for player in players:
        try:
            name = player.get('full_name', '')
            position = player.get('pos', '')
            total = player.get('total', '')
            topar = player.get('topar', '')
            status = player.get('status', '')
            
            print(f"{name:<30} {position:<10} {total:<10} {topar:<10} {status:<10}")
        except Exception as e:
            print(f"Error processing player: {str(e)}")
    
    # Display round information for the first player
    if players:
        print("\nDetailed Round Information for First Player:")
        first_player = players[0]
        print(f"Player: {first_player.get('full_name', '')}")
        
        for round_num in range(1, 5):
            round_key = f"round{round_num}"
            round_data = first_player.get(round_key, {})
            
            if round_data:
                print(f"\nRound {round_num}:")
                print(f"  Total: {round_data.get('total', '-')}")
                print(f"  Status: {round_data.get('roundStatus', '-')}")
                print(f"  Tee Time: {round_data.get('teetime', '-')}")
                
                scores = round_data.get('scores', [])
                if scores:
                    print("  Hole Scores:")
                    for hole, score in enumerate(scores, 1):
                        print(f"    Hole {hole}: {score}")

def export_to_excel(data, year=2025):
    """
    Export the Masters Tournament data to an Excel file with multiple sheets.
    
    Args:
        data (dict): The JSON data from the Masters Tournament API
        year (int): The year of the Masters Tournament
    """
    if not data:
        print("No data to export")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"masters_tournament_{year}_{timestamp}.xlsx"
    
    # Create Excel writer
    writer = pd.ExcelWriter(filename, engine='openpyxl')
    
    # Get player data
    players = data.get('data', {}).get('player', [])
    
    # Create leaderboard dataframe
    leaderboard_data = []
    for player in players:
        leaderboard_data.append({
            'Name': player.get('full_name', ''),
            'Position': player.get('pos', ''),
            'Total Score': player.get('total', ''),
            'To Par': player.get('topar', ''),
            'Status': player.get('status', ''),
            'Country': player.get('countryName', ''),
            'Amateur': 'Yes' if player.get('amateur', False) else 'No',
            'Tee Time': player.get('teetime', '')
        })
    
    leaderboard_df = pd.DataFrame(leaderboard_data)
    leaderboard_df.to_excel(writer, sheet_name='Leaderboard', index=False)
    
    # Create round-by-round dataframe
    rounds_data = []
    for player in players:
        player_rounds = {
            'Name': player.get('full_name', ''),
            'Total': player.get('total', ''),
            'To Par': player.get('topar', '')
        }
        
        # Add round data
        for round_num in range(1, 5):
            round_key = f'round{round_num}'
            round_data = player.get(round_key, {})
            player_rounds[f'R{round_num} Score'] = round_data.get('total', '-')
            player_rounds[f'R{round_num} Status'] = round_data.get('roundStatus', '-')
            player_rounds[f'R{round_num} Tee Time'] = round_data.get('teetime', '-')
    
        rounds_data.append(player_rounds)
    
    rounds_df = pd.DataFrame(rounds_data)
    rounds_df.to_excel(writer, sheet_name='Round Details', index=False)
    
    # Create hole-by-hole dataframe for each round
    for round_num in range(1, 5):
        round_key = f'round{round_num}'
        holes_data = []
        
        for player in players:
            round_data = player.get(round_key, {})
            scores = round_data.get('scores', [])
            
            if scores:
                hole_scores = {
                    'Name': player.get('full_name', ''),
                    'Round Total': round_data.get('total', '-')
                }
                
                # Add hole scores
                for hole, score in enumerate(scores, 1):
                    hole_scores[f'Hole {hole}'] = score
                
                holes_data.append(hole_scores)
        
        if holes_data:
            holes_df = pd.DataFrame(holes_data)
            holes_df.to_excel(writer, sheet_name=f'Round {round_num} Holes', index=False)
    
    # Create course info sheet
    course_data = data.get('data', {})
    yardages = course_data.get('yardages', {})
    pars = course_data.get('pars', {})
    
    course_info = []
    for hole in range(18):
        hole_info = {'Hole': hole + 1}
        for round_num in range(1, 5):
            round_key = f'round{round_num}'
            hole_info[f'R{round_num} Yardage'] = yardages.get(round_key, [])[hole] if hole < len(yardages.get(round_key, [])) else '-'
            hole_info[f'R{round_num} Par'] = pars.get(round_key, [])[hole] if hole < len(pars.get(round_key, [])) else '-'
        course_info.append(hole_info)
    
    course_df = pd.DataFrame(course_info)
    course_df.to_excel(writer, sheet_name='Course Info', index=False)
    
    # Save the Excel file
    writer.close()
    print(f"\nData exported to {filename}")
    
    return filename

def main():
    # Fetch data for 2025 Masters Tournament
    year = 2025
    data = fetch_masters_data(year)
    
    # Save the data to a file
    save_data_to_file(data, year)
    
    # Display player data
    display_player_data(data)
    
    # Print the full JSON structure
    if data:
        print("\nFull JSON Structure (first 1000 chars):")
        print(json.dumps(data, indent=2)[:1000] + "...")
    
    # Export to Excel
    if data:
        excel_file = export_to_excel(data, year)
        print(f"Excel file created: {excel_file}")
    else:
        print("Failed to fetch data")

if __name__ == "__main__":
    main() 