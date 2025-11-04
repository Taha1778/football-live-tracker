import requests

def fetch_match_id(team_id):
    api_key = "a051da316eb9e49d716c7d78f775e307"
    base_url = "https://v3.football.api-sports.io/"
    endpoint = "fixtures"

    # Fetch only live matches
    params = {"live": "all"}
    headers = {'x-apisports-key': api_key}

    try:
        response = requests.get(base_url + endpoint, params=params, headers=headers)
        response.raise_for_status()
        live_matches = response.json().get('response', [])

        # Find your team’s live match
        live_match = next(
            (m for m in live_matches
             if m['teams']['home']['id'] == team_id or m['teams']['away']['id'] == team_id),
            None
        )

        if live_match:
            match_id = live_match['fixture']['id']
            print(f"Match is live! Fixture ID: {match_id}")
            return match_id
        else:
            print("No match was found for this team today.")
            return None

    except Exception as e:
        print(f"Error fetching match data: {e}")
        return None
