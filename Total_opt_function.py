import time
import schedule
from fetch_id import fetch_match_id
from Get_new_events import get_new_events
from Message_generator import generate_message
from Notifier import send_telegram_message
import requests

match_id = None  # global variable

# --- New: runtime flags & config (minimal and contained) ---
RUNNING = True
HT_LOCK = False  # prevents re-triggering the 15-min pause multiple times
HALFTIME_INITIAL_PAUSE_MIN = 15  # first silent pause
TERMINAL_STATES = {"FT", "AET", "PEN", "ABD", "CANC", "PST"}  # safety enders

API_KEY = "a051da316eb9e49d716c7d78f775e307"
BASE_URL = "https://v3.football.api-sports.io/"
HEADERS = {'x-apisports-key': API_KEY}

def _get_status():
    """
    Minimal helper to fetch current fixture status.short for the active match_id.
    Returns: 'NS','1H','HT','2H','FT',... or None on error.
    """
    if not match_id:
        return None
    try:
        resp = requests.get(BASE_URL + "fixtures", params={"id": match_id}, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        fixture = data['response'][0]['fixture']
        return fixture['status']['short']
    except Exception as e:
        print(f"Error checking match status: {e}")
        return None

def _restart_updater():
    """Re-enable your normal periodic updater job (1/min), replacing any old one."""
    schedule.clear("updater")
    schedule.every(1).minutes.do(Updater).tag("updater")
    print("▶️ Resumed normal live polling (1/min).")

def _shutdown():
    """Stop everything cleanly when match ends (or terminal state is detected)."""
    global RUNNING, HT_LOCK
    RUNNING = False
    HT_LOCK = False
    schedule.clear()
    print("🛑 Match ended. Scheduler cleared and loop will exit.")

def _ht_probe():
    """
    One-shot probe:
      - After the initial 15-min pause, check status once.
      - If still HT -> schedule another probe after 1 minute.
      - If 2H (or any non-HT live) -> resume updater and clear lock.
      - If terminal -> shutdown.
    Always returns schedule.CancelJob to keep this as a one-shot.
    """
    status = _get_status()
    if status in TERMINAL_STATES:
        _shutdown()
        return schedule.CancelJob

    if status == "HT":
        # Still halftime: check again in 1 minute (1 request/min)
        schedule.clear("ht_probe")
        schedule.every(1).minutes.do(_ht_probe).tag("ht_probe")
        print("⏳ Still halftime after initial pause. Will probe again in 1 minute.")
        return schedule.CancelJob

    # 2H (or any non-HT live state): resume normal polling
    global HT_LOCK
    HT_LOCK = False
    schedule.clear("ht_probe")
    _restart_updater()
    return schedule.CancelJob

def Updater():
    global match_id, HT_LOCK
    print("Updating...")
    if not match_id:
        print("⚠️ No match ID yet. Skipping update.")
        return

    # --- Fetch current match status ONCE per tick ---
    status_short = _get_status()

    # --- Stop everything if terminal state is reached ---
    if status_short in TERMINAL_STATES:
        _shutdown()
        return

    # --- New halftime flow (preserve your behavior but without double-pausing) ---
    if status_short == "HT":
        if not HT_LOCK:
            # First time we hit halftime: stop normal updater and wait 15 minutes (no requests)
            HT_LOCK = True
            print(f"⏸️ Match is at halftime. Pausing all polling for {HALFTIME_INITIAL_PAUSE_MIN} minutes...")
            schedule.clear("updater")              # stop periodic requests
            schedule.clear("ht_probe")
            # After 15 minutes, do ONE probe; if still HT, switch to 1/min probes
            schedule.every(HALFTIME_INITIAL_PAUSE_MIN).minutes.do(_ht_probe).tag("ht_probe")
        # During halftime lock, skip fetching events entirely
        return

    # --- Normal live flow: fetch events and notify ---
    new_events = get_new_events(match_id)
    if new_events:
        message = generate_message(new_events)
        if message:
            send_telegram_message(message)

def fetch_and_update_match(team_id):
    global match_id
    new_match_id = fetch_match_id(team_id)
    if new_match_id != match_id:
        print(f"✅ New match found! ID = {new_match_id}")
        match_id = new_match_id
    else:
        print("No new live match found.")

def total_opt_function(team_id):
    global RUNNING
    # Fetch immediately at startup
    fetch_and_update_match(team_id)
    # Schedule regular updates
    schedule.every(1).minutes.do(Updater).tag("updater")      # tag added (minimal change)
    schedule.every(1).hours.do(fetch_and_update_match, team_id)
    print("✅ Schedulers set up successfully!")

    # Run loop until a terminal state shuts us down
    while RUNNING:
        schedule.run_pending()
        time.sleep(1)
