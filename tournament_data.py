import json
import os

TOURNAMENT_FILE = "tournaments.json"
_tournaments = None

def load_tournaments():
    global _tournaments
    if _tournaments is None:
        if os.path.exists(TOURNAMENT_FILE):
            with open(TOURNAMENT_FILE, "r") as f:
                _tournaments = json.load(f)
        else:
            _tournaments = {}
    return _tournaments

def save_tournaments(data):
    with open(TOURNAMENT_FILE, "w") as f:
        json.dump(_tournaments, f, indent=4)
