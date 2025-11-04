import requests

seen_events = set()

def get_new_events(required_match_id):
    global seen_events

    api_key = "a051da316eb9e49d716c7d78f775e307"
    base_url = "https://v3.football.api-sports.io/"
    headers = {'x-apisports-key': api_key}

    endpoint_events = "fixtures/events"
    params_events = {"fixture": required_match_id}

    try:
        response = requests.get(base_url + endpoint_events, params=params_events, headers=headers)
        response.raise_for_status()
        events = response.json().get('response', [])
    except Exception as e:
        print(f"An error occurred while fetching events: {e}")
        return []

    new_events = []
    for event in events:
        time_elapsed = event.get('time', {}).get('elapsed', 0)
        team_name = event.get('team', {}).get('name')
        player_name = event.get('player', {}).get('name')
        event_type = event.get('type')
        detail = event.get('detail')

        event_key = (time_elapsed, team_name, player_name, event_type, detail)

        if event_key not in seen_events:
            seen_events.add(event_key)

            # Handle substitutions safely
            if event_type and event_type.lower() == "substitution":
                in_player = event.get('assist', {}).get('name', "Unknown")
                event['sub_in'] = in_player

            new_events.append(event)

    if new_events:
        print(f"✅ {len(new_events)} new event(s) found for match {required_match_id}.")
    else:
        print(f"ℹ️ No new events for match {required_match_id}.")

    return new_events
