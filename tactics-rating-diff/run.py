"""
Gets the peak rapid, blitz, and tactics ratings for all titled players on chess.com.
"""

import json
import os

import requests
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt


def get_titled_players() -> list:
    players = []
    for title in ["GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM"]:
        response = requests.get(f"https://api.chess.com/pub/titled/{title}").json()
        players.extend(response["players"])

    players.sort()

    return players


data = []

if os.path.exists("titled_player_data.json"):
    data = json.load(open("titled_player_data.json"))

processed_players = set([r["username"] for r in data])

titled_players = get_titled_players()

for player in tqdm(titled_players):
    if player in processed_players:
        continue

    stats = requests.get(f"https://api.chess.com/pub/player/{player}/stats").json()
    if "tactics" not in stats or "chess_rapid" not in stats or "chess_blitz" not in stats:
        continue

    if sum(stats["chess_rapid"]["record"].values()) < 25:
        continue

    if sum(stats["chess_blitz"]["record"].values()) < 25:
        continue

    try:
        tactics_peak = stats["tactics"]["highest"]["rating"]
        rapid_peak = stats["chess_rapid"]["best"]["rating"]
        blitz_peak = stats["chess_blitz"]["best"]["rating"]
    except KeyError as e:
        print(json.dumps(stats, indent=2))
        raise KeyError(e)

    data.append({
        "username": player,
        "rapid": rapid_peak,
        "blitz": blitz_peak,
        "tactics": tactics_peak,
        "tactics_diff": tactics_peak - rapid_peak,
    })

    json.dump(data, open("titled_player_data.json", "w"))

df = pd.DataFrame(data)
df.to_csv("titled_player_ratings.csv", index=False)

plt.hist(df["tactics_diff"], bins='auto')
plt.title("Tactics Rating - Rapid Rating")
plt.show()
