from typing import NamedTuple
from datetime import datetime
from pathlib import Path
import json

import requests
import pandas as pd
import matplotlib.pyplot as plt


mapping = {
    "win": 1,
    "checkmated": 0,
    "agreed": 0.5,
    "repetition": 0.5,
    "timeout": 0,
    "resigned": 0,
    "stalemate": 0.5,
    "lose": 0,
    "insufficient": 0.5,
    "50move": 0.5,
    "abandoned": 0,
    "timevsinsufficient": 0.5,
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


def expected_score(opponent_ratings: list[float], own_rating: float) -> float:
    """How many points we expect to score in games with these opponents"""
    return sum(
        1 / (1 + 10 ** ((opponent_rating - own_rating) / 400))
        for opponent_rating in opponent_ratings
    )


def performance_rating(opponent_ratings: list[float], score: float) -> int:
    """Calculate mathematically perfect performance rating with binary search."""
    lo, hi = 0, 10000

    while hi - lo > 0.0001:
        mid = (lo + hi) / 2

        if expected_score(opponent_ratings, mid) < score:
            lo = mid
        else:
            hi = mid

    return round(mid)


def get_top_players():
    response = requests.get("https://api.chess.com/pub/leaderboards", headers=HEADERS)
    blitz_players = response.json()["live_blitz"]
    return [player["username"] for player in blitz_players]


class Result(NamedTuple):
    rating: int
    result: float
    date: datetime
    url: str
    opponent: str


def main(username, time_control="blitz"):
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    archives = requests.get(url, headers=HEADERS)
    try:
        archives = archives.json()["archives"]
    except Exception:
        print(archives.text)
        print(archives.url)
    archives.sort()

    rating_results: list[Result] = []

    for url in archives[:-1]:
        save_path = Path("data") / username
        if not save_path.exists():
            save_path.mkdir(parents=True)

        save_name = f'{"_".join(url.split("/")[-2:])}.json'

        if (save_path / save_name).exists():
            archive_response = json.load(open(save_path / save_name))
        else:
            archive_response = requests.get(url, headers=HEADERS).json()
            with open(save_path / save_name, "w+") as out:
                json.dump(archive_response, out)

        if "games" not in archive_response:
            continue

        for game_json in archive_response["games"]:
            # not a rated game
            if not game_json["rated"]:
                continue

            # must be a blitz game
            if game_json["time_control"] != "180":
                continue

            # if the initial setup isn't a usual game of chess
            if game_json["rules"] != "chess":
                continue

            opponent = (
                "black"
                if username.lower() == game_json["white"]["username"].lower()
                else "white"
            )

            rating_results.append(
                Result(
                    float(game_json[opponent]["rating"]),
                    1.0 - mapping[game_json[opponent]["result"]],
                    datetime.fromtimestamp(game_json["end_time"]),
                    game_json["url"],
                    game_json[opponent]["username"],
                )
            )

    diff = 46

    performances = [
        performance_rating(
            [result.rating for result in rating_results[x : x + diff]],
            sum(result.result for result in rating_results[x : x + diff]),
        )
        for x in range(len(rating_results) - diff)
    ]

    count = sum(1 for x in performances if x >= 7000)

    df = pd.DataFrame(
        {
            "games": [x for x in range(len(rating_results) - diff)],
            "performance": performances,
        }
    )
    df.plot(x="games", y="performance")
    plt.show()

    print(f"{username}|{max(performances) if performances else 0}|{count}")

    return performances


if __name__ == "__main__":
    top_players = get_top_players()
    top_players = ['Hikaru']

    for player in top_players:
        main(player)
