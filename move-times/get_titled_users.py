"""
Get the top players (by username) for a given game format.
"""

import json

import requests
from tqdm import tqdm

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


def get_titled_players() -> list:
    players = []
    for title in ["GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM"]:
        response = requests.get(f"https://api.chess.com/pub/titled/{title}", headers=HEADERS).json()
        players.extend(response["players"])

    return players


def main():
    titled_players = get_titled_players()
    output = json.loads(open("titled_players.json", "r").read())

    for i, player in tqdm(enumerate(titled_players)):
        if player in output:
            continue

        response = requests.get(f"https://api.chess.com/pub/player/{player}", headers=HEADERS)
        output[player] = response.json()
        if i % 100 == 0:
            with open("titled_players.json", "w") as f:
                f.write(json.dumps(output))


if __name__ == '__main__':
    main()
