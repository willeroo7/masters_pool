import pandas as pd
import os

def extract_teams_data():
    """
    Extracts teams data from the Excel file up to the 'End' marker.
    Returns a clean DataFrame with specified columns.
    """
    # Set display options for better readability
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    
    # Path to the example file
    example_file_path = os.path.join('examples', 'masters_setup_2025.xlsx')
    
    try:
        # Read the Teams sheet
        df = pd.read_excel(example_file_path, sheet_name='Teams')
        
        # Debug: Print unique values in Paid column
        print("Unique values in Paid column:", df['Paid'].unique())
        
        # Find the index where 'Paid' column contains 'End'
        end_rows = df[df['Paid'].astype(str).str.lower() == 'end']
        if len(end_rows) > 0:
            end_idx = end_rows.index[0]
            # Slice the dataframe up to the 'End' marker
            df = df.iloc[:end_idx]
        else:
            print("Warning: No 'End' marker found in Paid column. Using all rows.")
        
        # Rename columns to match desired format
        column_mapping = {
            'Paid': 'Paid',
            'Team #': 'Team #',
            'Name': 'Name',
            'Tie Breaker': 'Tie Breaker',
            1: 'Tier 1',
            2: 'Tier 2',
            3: 'Tier 3',
            4: 'Tier 4',
            5: 'Tier 5',
            6: 'Tier 6'
        }
        
        # Select and rename only the columns we want
        teams_df = df[list(column_mapping.keys())].rename(columns=column_mapping)
        
        return teams_df
        
    except Exception as e:
        print(f"Error extracting teams data: {str(e)}")
        return None

if __name__ == "__main__":
    # Extract the data
    teams_df = extract_teams_data()
    
    if teams_df is not None:
        # Display all columns with proper formatting
        print("\nExtracted Teams Data:")
        print(teams_df.to_string(index=True))
        
        # Save to Excel file
        output_file = os.path.join('examples', 'participants_teams.xlsx')
        teams_df.to_excel(output_file, index=False, sheet_name='Teams')
        print(f"\nData saved to: {output_file}") 