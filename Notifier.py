import requests
def send_telegram_message(message):
    chat_id=2058609968
    api='8462803145:AAFtrE0NPOizQZ7xyGO3QklxXHVL25FNPCQ'
    url = f"https://api.telegram.org/bot{api}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response.json()



