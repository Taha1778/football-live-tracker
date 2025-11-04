
import requests
import json
import pandas as pd
api_key = "a051da316eb9e49d716c7d78f775e307"
base_url = "https://v3.football.api-sports.io/"

# Endpoint to get matches that are currently LIVE
endpoint = "fixtures" # The documentation often uses 'fixtures' but filtering by 'live' status is the key.

# Use the 'live' parameter to only get matches currently in progress
params = {
    # Request fixtures with a 'live' status
    "live": "all",
    # OPTIONAL: You can filter by a league ID if you know which leagues are live and accessible
    # "league": 39 # Example: Premier League ID (Use with caution based on plan access)
}

headers = {'x-apisports-key': api_key}

try:
    response = requests.get(base_url + endpoint, params=params, headers=headers)
    response.raise_for_status()
    live_matches = response.json().get('response', [])

    if live_matches:
        print(f"Found {len(live_matches)} LIVE matches currently in progress on your plan.")
        print("Here are the live matches:")
        
        
        for match in live_matches:
            fixture = match['fixture']
            teams = match['teams']
            #turn fixtures into a pandas dataframe
            
            #save match id if the home or away team is Hungary
            
            required_match_id = fixture['id']
            print(f"Fixture ID: {fixture['id']}, {teams['home']['name']} vs {teams['away']['name']}, Status: {fixture['status']['long']}")
            
        
        # Now, you can easily find your team's live match ID from this filtered list:
        
        team_id_rm = 55
        live_id = next((f['fixture']['id'] for f in live_matches 
                        if f['teams']['home']['id'] == team_id_rm or f['teams']['away']['id'] == team_id_rm), None)

        if live_id:
            print(f"SUCCESS! Real Madrid's live Fixture ID is: {live_id}")
            # Proceed to the event tracker loop with this ID
        else:
            print("Real Madrid is not in the list of currently live matches.")
            
    else:
        print("No matches are currently live or available on your free plan right now.")
        
except Exception as e:
    print(f"An error occurred: {e}")


#find the required match id score and events
