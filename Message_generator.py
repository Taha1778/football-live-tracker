def generate_message(new_events):
    message = ""
    for event in new_events:
        if event['type'].lower() == "substitution" or event['type'].lower() == "subst":
            message += f"Time: {event['time']['elapsed']}' - {event['team']['name']} - {event['player']['name']} OUT, {event.get('sub_in', 'Unknown')} IN\n"
        else:
            message += f"Time: {event['time']['elapsed']}' - {event['team']['name']} - {event['player']['name']} - {event['type']} - {event['detail']}\n"
    return message
