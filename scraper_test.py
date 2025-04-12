import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json

class MastersScraper:
    def __init__(self):
        # Using official Masters Tournament API for 2025
        self.base_url = "https://www.masters.com/en_US/scores/feeds/2025/scores.json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.masters.com/'
        }

    def get_scores(self):
        """
        Fetches live scores from the Masters Tournament API.
        Returns a list of dictionaries containing player data.
        """
        try:
            print("Attempting to fetch scores from Masters Tournament API...")
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            print(f"API Response Status: {response.status_code}")
            
            scores_data = []
            players = data.get('data', {}).get('player', [])
            
            for player in players:
                try:
                    # Get round data
                    round_scores = {}
                    for round_num in range(1, 5):
                        round_key = f'round{round_num}'
                        round_data = player.get(round_key, {})
                        round_status = round_data.get('roundStatus', 'Pre')
                        
                        if round_status == 'Finished':
                            round_scores[round_key] = {
                                'score': str(round_data.get('total', '-')),
                                'status': round_status,
                                'relative_to_par': round_data.get('fantasy', 0)
                            }
                        elif round_status == 'Playing':
                            round_scores[round_key] = {
                                'score': str(round_data.get('fantasy', '-')),
                                'status': round_status,
                                'relative_to_par': round_data.get('fantasy', '0')  # Just use fantasy field
                            }
                        else:
                            round_scores[round_key] = {
                                'score': '-',
                                'status': round_status,
                                'relative_to_par': 0
                            }
                    
                    player_data = {
                        'name': player.get('full_name', ''),
                        'position': player.get('pos', ''),
                        'total_score': player.get('topar', ''),
                        'rounds': round_scores,
                        'status': player.get('status', ''),
                        'country': player.get('countryCode', ''),
                        'is_amateur': player.get('amateur', False),
                        'is_past_champion': player.get('past', False)
                    }
                    scores_data.append(player_data)
                except Exception as e:
                    print(f"Error processing player data: {str(e)}")
                    continue
            
            if not scores_data:
                print("No player data found in the API response")
                return self.get_sample_data()
            
            print(f"Successfully fetched data for {len(scores_data)} players")
            return scores_data
            
        except requests.RequestException as e:
            print(f"Error fetching scores: {str(e)}")
            print(f"Response content: {response.text if 'response' in locals() else 'No response'}")
            return self.get_sample_data()
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {str(e)}")
            return self.get_sample_data()
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return self.get_sample_data()
    
    def get_sample_data(self):
        """
        Returns sample data for development and testing purposes.
        """
        print("Using sample data due to API error")
        return [
            {
                'name': 'Scottie Scheffler',
                'position': '1',
                'total_score': '-7',
                'rounds': {
                    'round1': '66',
                    'round2': '72',
                    'round3': '71',
                    'round4': '-'
                },
                'status': 'Active',
                'country': 'USA',
                'is_amateur': False,
                'is_past_champion': True
            },
            {
                'name': 'Collin Morikawa',
                'position': '2',
                'total_score': '-6',
                'rounds': {
                    'round1': '71',
                    'round2': '70',
                    'round3': '69',
                    'round4': '-'
                },
                'status': 'Active',
                'country': 'USA',
                'is_amateur': False,
                'is_past_champion': False
            },
            {
                'name': 'Max Homa',
                'position': 'T3',
                'total_score': '-5',
                'rounds': {
                    'round1': '67',
                    'round2': '71',
                    'round3': '73',
                    'round4': '-'
                },
                'status': 'Active',
                'country': 'USA',
                'is_amateur': False,
                'is_past_champion': False
            }
        ]

def create_debug_dataframe(scores_data):
    """
    Creates a pandas DataFrame for debugging purposes.
    Shows raw data for each round and player.
    """
    debug_data = []
    
    for player in scores_data:
        player_info = {
            'Name': player['name'],
            'Position': player['position'],
            'Total Score': player['total_score'],
            'Status': player['status'],
            'Country': player['country']
        }
        
        # Add round information
        for round_num in range(1, 5):
            round_key = f'round{round_num}'
            round_data = player['rounds'][round_key]
            
            player_info[f'Round {round_num} Score'] = round_data['score']
            player_info[f'Round {round_num} Status'] = round_data['status']
            player_info[f'Round {round_num} To Par'] = round_data['relative_to_par']
        
        debug_data.append(player_info)
    
    return pd.DataFrame(debug_data)

if __name__ == "__main__":
    # Create scraper instance
    scraper = MastersScraper()
    
    # Get scores
    scores = scraper.get_scores()
    
    # Create debug DataFrame
    df = create_debug_dataframe(scores)
    
    # Print DataFrame
    print("\nDebug DataFrame:")
    print(df.to_string())
    
    # Save DataFrame to Excel
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f'masters_scores_{current_time}.xlsx'
    df.to_excel(excel_filename, index=False)
    print(f"\nScores saved to Excel file: {excel_filename}")
    
    # Print raw data for first player's round 3
    print("\nRaw Round 3 Data for First Player:")
    first_player = scores[0]
    round3_data = first_player['rounds']['round3']
    print(f"Round 3 Score: {round3_data['score']}")
    print(f"Round 3 Status: {round3_data['status']}")
    print(f"Round 3 To Par: {round3_data['relative_to_par']}")
    
    # Print raw API data for first player's round 3
    print("\nRaw API Data for First Player's Round 3:")
    response = requests.get(scraper.base_url, headers=scraper.headers)
    data = response.json()
    first_player_raw = data['data']['player'][0]
    print(f"Round 3 Raw Data: {first_player_raw.get('round3', {})}") 