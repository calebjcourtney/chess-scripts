"""
Get the top players (by username) for a given game format.
"""

import argparse
import json

import requests


def get_top_players(game_format) -> list:
    response = requests.get("https://api.chess.com/pub/leaderboards").json()
    if game_format not in response:
        raise ValueError(f"Invalid game format: must be one of {', '.join(response.keys())}")

    return [player["username"] for player in response[game_format]]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("game_format", type=str)

    args = parser.parse_args()

    print(json.dumps(get_top_players(args.game_format)))
