import random
import os
import json

import pandas as pd
from tqdm import tqdm
import requests
from statistics import median
from statistics import stdev
from scipy.stats import pearsonr

# Seed for reproducibility
# jan 23 2024
random.seed(1 + 23 + 2024)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

TOURNAMENT_ID_CONTAINS = "titled-tuesday"
TIME_CONTROL = "blitz"


GAME_CODES = {
    "win": "win",
    "checkmated": "lose",
    "agreed": "draw",
    "repetition": "draw",
    "timeout": "lose",
    "resigned": "lose",
    "stalemate": "draw",
    "lose": "lose",
    "insufficient": "draw",
    "50move": "draw",
}


ARCHIVE_FILES = os.listdir("user_archives")


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


def get_tournament_players() -> list[str]:
    players = set()
    for url in TOURNAMENT_URLS:
        response = requests.get(url, headers=HEADERS)
        blitz_players = response.json()["players"]
        players |= {player["username"] for player in blitz_players}

    return players


def get_user_archives(username):
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    archives = requests.get(url, headers=HEADERS)
    archives = archives.json().get("archives", [])
    archives.sort()

    return archives


def get_tt_games(username):
    archives = get_user_archives(username)[-12:]
    for url in archives:
        file_name = "_".join(url.split("/")[-6:]) + ".json"
        if file_name not in os.listdir("user_archives") or file_name == archives[-1]:
            response = requests.get(url, headers=HEADERS)
            with open(f"user_archives/{file_name}", "w") as f:
                f.write(response.text)


def get_rating_corr():
    tt_elo_accuracy: list[tuple[int, float]] = []
    elo_accuracy: list[tuple[int, float]] = []
    for file_name in tqdm(ARCHIVE_FILES):
        games = json.load(open(f"user_archives/{file_name}", "r"))["games"]
        for game in games:
            if "accuracies" not in game:
                continue

            if "tournament" in game and TOURNAMENT_ID_CONTAINS in game["tournament"]:
                tt_elo_accuracy.append((game["white"]["rating"], game["accuracies"]["white"]))
                tt_elo_accuracy.append((game["black"]["rating"], game["accuracies"]["black"]))

            else:
                elo_accuracy.append((game["white"]["rating"], game["accuracies"]["white"]))
                elo_accuracy.append((game["black"]["rating"], game["accuracies"]["black"]))

    print(f"TT ELO ACCURACY CORRELATION: {pearsonr(*zip(*tt_elo_accuracy))}")
    print(f"ELO ACCURACY CORRELATION: {pearsonr(*zip(*elo_accuracy))}")


def analyze_data(username, opponents):
    files = [filename for filename in ARCHIVE_FILES if f"_{username}_" in filename]

    output = {opp: {"win": 0, "lose": 0, "draw": 0} for opp in opponents}

    for file_name in files:
        with open(f"user_archives/{file_name}", "r") as month_data:
            games = json.load(month_data)["games"]
            for game in games:
                color = (
                    "white"
                    if username.lower() == game["white"]["username"].lower()
                    else "black"
                )
                opponent = game["black" if color == "white" else "white"]["username"]
                if opponent.lower() not in opponents:
                    continue

                result = GAME_CODES.get(game[color]["result"], "other")

                if (
                    "tournament" in game
                    and TOURNAMENT_ID_CONTAINS in game["tournament"]
                ):
                    output[opponent.lower()][result] += 1

    return output


def summarize_data(player_results: list[dict[str, list]]):
    summary = {
        "tt_win_accuracies": [],
        "tt_loss_accuracies": [],
        "tt_draw_accuracies": [],
        "win_accuracies": [],
        "loss_accuracies": [],
        "draw_accuracies": [],
    }
    for res in player_results:
        summary["tt_win_accuracies"].append(
            sum(res["tt_win_accuracies"]) / len(res["tt_win_accuracies"])
        )
        summary["tt_loss_accuracies"].append(
            sum(res["tt_loss_accuracies"]) / len(res["tt_loss_accuracies"])
        )

        if res["tt_draw_accuracies"]:
            summary["tt_draw_accuracies"].append(
                sum(res["tt_draw_accuracies"]) / len(res["tt_draw_accuracies"])
            )

        summary["win_accuracies"].append(
            sum(res["win_accuracies"]) / len(res["win_accuracies"])
        )
        summary["loss_accuracies"].append(
            sum(res["loss_accuracies"]) / len(res["loss_accuracies"])
        )

        if res["draw_accuracies"]:
            summary["draw_accuracies"].append(
                sum(res["draw_accuracies"]) / len(res["draw_accuracies"])
            )

    return {
        "tt_win_accuracies": {
            "average": round(sum(summary["tt_win_accuracies"]) / len(summary["tt_win_accuracies"]), 2),
            "median": round(median(summary["tt_win_accuracies"]), 2),
            "stdev": round(stdev(summary["tt_win_accuracies"]), 2),
        },
        "tt_loss_accuracies": {
            "average": round(sum(summary["tt_loss_accuracies"]) / len(summary["tt_loss_accuracies"]), 2),
            "median": round(median(summary["tt_loss_accuracies"]), 2),
            "stdev": round(stdev(summary["tt_loss_accuracies"]), 2),
        },
        "tt_draw_accuracies": {
            "average": round(sum(summary["tt_draw_accuracies"]) / len(summary["tt_draw_accuracies"]), 2),
            "median": round(median(summary["tt_draw_accuracies"]), 2),
            "stdev": round(stdev(summary["tt_draw_accuracies"]), 2),
        },
        "win_accuracies": {
            "average": round(sum(summary["win_accuracies"]) / len(summary["win_accuracies"]), 2),
            "median": round(median(summary["win_accuracies"]), 2),
            "stdev": round(stdev(summary["win_accuracies"]), 2),
        },
        "loss_accuracies": {
            "average": round(sum(summary["loss_accuracies"]) / len(summary["loss_accuracies"]), 2),
            "median": round(median(summary["loss_accuracies"]), 2),
            "stdev": round(stdev(summary["loss_accuracies"]), 2),
        },
        "draw_accuracies": {
            "average": round(sum(summary["draw_accuracies"]) / len(summary["draw_accuracies"]), 2),
            "median": round(median(summary["draw_accuracies"]), 2),
            "stdev": round(stdev(summary["draw_accuracies"]), 2),
        },
    }


def count_tt_games(player):
    count = 0
    for file_name in os.listdir("user_archives"):
        if f"_{player}_" in file_name:
            data = json.load(open(f"user_archives/{file_name}"))
            for game in data["games"]:
                if game["time_control"] == "180+1":
                    print(game)
                    count += 1

    return count


def main():
    # players = get_tournament_players()
    players = ['penguingm1']

    # for username in tqdm(players):
    #     get_tt_games(username)

    results: list[dict[str, list]] = []

    opponents = [
        "magnuscarlsen",
        "hikaru",
        "firouzja2003",
        "polish_fighter3000",
        "lachesisq",
        "fabianocaruana",
        "gmwso",
        "duhless",
        "oleksandr_bortnyk",
        "lyonbeast",
    ]

    user_games_data = analyze_data('penguingm1', opponents)
    print(user_games_data)

    output = []
    for opponent, values in user_games_data.items():
        values["opponent"] = opponent
        output.append(values)

    df = pd.DataFrame(output)
    print(df)




if __name__ == "__main__":
    main()
