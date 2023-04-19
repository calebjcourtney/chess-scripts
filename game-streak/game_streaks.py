"""
Get the player with the longest streak of wins in the given format.
"""

import argparse
import json
import os
import re

from tqdm import tqdm
import requests

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


def main() -> None:
    titled_players = get_titled_players()

    if os.path.exists("data.json"):
        with open("data.json", "r") as in_file:
            processed_info = json.load(in_file)
            longest_streak = processed_info["longest_streak"]
            title_holders = processed_info["title_holders"]

    else:
        longest_streak = 0
        title_holders = []

    for player in tqdm(titled_players):
        if any([player < holder for holder in title_holders]):
            continue

        stats_raw = requests.get(f"https://www.chess.com/stats/live/{args.format}/{player}/0").text
        result = streak_find.search(stats_raw)
        if result is None:
            continue

        player_longest_streak = 0 if result.group(1) is None else int(result.group(1))

        if player_longest_streak > longest_streak:
            longest_streak = player_longest_streak
            title_holders = [player]

        elif player_longest_streak == longest_streak:
            title_holders.append(player)

        with open("data.json", "w+") as out_file:
            json.dump(
                {
                    "longest_streak": longest_streak,
                    "title_holders": title_holders
                },
                out_file
            )

    print(f"Longest streak of wins: {longest_streak}")
    print(f"Usernames holding record: {', '.join(title_holders)}")


if __name__ == '__main__':
    main()
