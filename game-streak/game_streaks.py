"""
Get the player with the longest streak of wins in the given format.
"""
from typing import Tuple

import argparse
import json
import re
import sys

import requests
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("format", type=str, choices=["bullet", "blitz", "rapid"])
args = parser.parse_args()

streak_find = re.compile(r'"winningStreak":(\d+)')


def get_titled_players() -> list:
    players = []
    for title in ["GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM"]:
        response = requests.get(f"https://api.chess.com/pub/titled/{title}").json()
        players.extend(response["players"])

    players.sort()

    return players


def get_user_streak(fmt: str, username: str) -> Tuple[str, int]:
    response = requests.get(f"https://www.chess.com/stats/live/{fmt}/{username}/0")
    assert response.status_code == 200

    stats_raw = response.text
    result = streak_find.search(stats_raw)
    if result is None:
        return {
            "username": username,
            "streak": 0
        }

    streak = int(result.group(1))

    return {
        "username": username,
        "streak": streak
    }


def main() -> None:
    titled_players = get_titled_players()

    processed_data = json.load(open("data.json", "r"))
    processed_players = [player["username"] for player in processed_data]

    for player in tqdm(titled_players):
        if player in processed_players:
            continue

        response = get_user_streak(args.format, player)
        processed_data.append(response)

        with open("data.json", "w+") as out_file:
            json.dump(processed_data, out_file, indent=2)

    processed_data.sort(key=lambda x: x["streak"], reverse=True)
    with open("data.json", "w+") as out_file:
        json.dump(processed_data, out_file)

    print(processed_data[0], file=sys.stderr)


if __name__ == '__main__':
    main()
