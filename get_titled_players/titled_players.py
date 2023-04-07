"""
Get the top players (by username) for a given game format.
"""

import json

import requests


def get_titled_players() -> list:
    players = []
    for title in ["GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM"]:
        response = requests.get(f"https://api.chess.com/pub/titled/{title}").json()
        players.extend(response["players"])

    return players


if __name__ == '__main__':
    print(json.dumps(get_titled_players()))
