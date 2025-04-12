import requests
import json
from collections import Counter
from datetime import datetime
import pandas as pd

class MastersScraper:
    def __init__(self):
        self.base_url = "https://www.masters.com/en_US/scores/feeds/2024/scores.json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.masters.com/'
        }

    def get_scores(self):
        try:
            print("Fetching scores from Masters Tournament API...")
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            players = data.get('data', {}).get('player', [])
            if not players:
                return self.get_sample_data()
            
            return players
            
        except Exception as e:
            print(f"Error fetching scores: {str(e)}")
            return self.get_sample_data()
    
    def get_sample_data(self):
        print("Using sample data")
        return [
            {
                'full_name': 'Scottie Scheffler',
                'round1': {'roundStatus': 'Finished'},
                'round2': {'roundStatus': 'Finished'},
                'round3': {'roundStatus': 'Playing'},
                'round4': {'roundStatus': 'Pre'}
            },
            {
                'full_name': 'Collin Morikawa',
                'round1': {'roundStatus': 'Finished'},
                'round2': {'roundStatus': 'Finished'},
                'round3': {'roundStatus': 'Playing'},
                'round4': {'roundStatus': 'Pre'}
            }
        ]

def show_round_status():
    scraper = MastersScraper()
    players = scraper.get_scores()
    
    # Create a list to store player data for DataFrame
    player_data = []
    
    print("\nRound Status for Each Player:")
    print("-" * 80)
    print(f"{'Player':<30} {'Rd1':<10} {'Rd2':<10} {'Rd3':<10} {'Rd4':<10}")
    print("-" * 80)
    
    all_finished = True
    
    for player in players:
        name = player.get('full_name', '')
        rd1 = player.get('round1', {}).get('roundStatus', 'N/A')
        rd2 = player.get('round2', {}).get('roundStatus', 'N/A')
        rd3 = player.get('round3', {}).get('roundStatus', 'N/A')
        rd4 = player.get('round4', {}).get('roundStatus', 'N/A')
        
        # Check if any round is not Finished
        if any(status != 'Finished' for status in [rd1, rd2, rd3, rd4]):
            all_finished = False
        
        # Add data to list for DataFrame
        player_data.append({
            'Player': name,
            'Round 1': rd1,
            'Round 2': rd2,
            'Round 3': rd3,
            'Round 4': rd4
        })
        
        print(f"{name:<30} {rd1:<10} {rd2:<10} {rd3:<10} {rd4:<10}")
    
    print("\n" + "-" * 80)
    print(f"All players finished all rounds: {all_finished}")
    
    # Create DataFrame and export to Excel
    df = pd.DataFrame(player_data)
    
    # Create Excel writer object
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = f'masters_round_status_{timestamp}.xlsx'
    
    # Create a writer object
    writer = pd.ExcelWriter(excel_file, engine='openpyxl')
    
    # Write the DataFrame to Excel
    df.to_excel(writer, sheet_name='Round Status', index=False)
    
    # Get the workbook and the worksheet
    workbook = writer.book
    worksheet = writer.sheets['Round Status']
    
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

if __name__ == "__main__":
    show_round_status() 