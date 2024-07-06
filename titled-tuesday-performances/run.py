import random
import os
import json

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
TOURNAMENT_URLS = [
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-january-02-2024-4490237/11",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-january-02-2024-4490238/11",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-january-09-2024-4490239/11",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-january-09-2024-4490240/11",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-january-16-2024-4503497/11",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-january-16-2024-4503498/11",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-january-23-2024-4518064/11",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-january-23-2024-4518065/11",
]
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


print("vs 2216: ", expected_score([2216], 1932))
print("vs 1874: ", expected_score([1874], 1932))
print("vs 1731: ", expected_score([1731], 1932))
print("vs all:", expected_score([2216, 1874, 1731], 1932))


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


print(performance_rating([2216, 1874, 1731], 1.5))


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
    archives = get_user_archives(username)[-3:]
    for url in archives:
        file_name = "_".join(url.split("/")[-6:]) + ".json"
        if file_name not in os.listdir("user_archives"):
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


def analyze_data(username):
    files = [filename for filename in ARCHIVE_FILES if username in filename]

    games_data = {
        "tt_win_accuracies": [],
        "tt_draw_accuracies": [],
        "tt_loss_accuracies": [],
        "win_accuracies": [],
        "draw_accuracies": [],
        "loss_accuracies": [],
    }

    for file_name in files:
        with open(f"user_archives/{file_name}", "r") as month_data:
            games = json.load(month_data)["games"]
            for game in games:
                if "accuracies" not in game:
                    continue

                color = (
                    "white"
                    if username.lower() == game["white"]["username"].lower()
                    else "black"
                )
                result = GAME_CODES.get(game[color]["result"], "other")

                if (
                    "tournament" in game
                    and TOURNAMENT_ID_CONTAINS in game["tournament"]
                ):
                    if result == "win":
                        games_data["tt_win_accuracies"].append(
                            game["accuracies"][color]
                        )
                    elif result == "lose":
                        games_data["tt_loss_accuracies"].append(
                            game["accuracies"][color]
                        )
                    elif result == "draw":
                        games_data["tt_draw_accuracies"].append(
                            game["accuracies"][color]
                        )
                else:
                    if result == "win":
                        games_data["win_accuracies"].append(game["accuracies"][color])
                    elif result == "lose":
                        games_data["loss_accuracies"].append(game["accuracies"][color])
                    elif result == "draw":
                        games_data["draw_accuracies"].append(game["accuracies"][color])

    return games_data


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


def main():
    players = get_tournament_players()

    # for username in tqdm(players):
    #     get_tt_games(username)

    results: list[dict[str, list]] = []

    for username in tqdm(players):
        user_games_data = analyze_data(username)
        enough_games = all(
            [
                (
                    len(user_games_data["tt_win_accuracies"])
                    + len(user_games_data["tt_loss_accuracies"])
                    + len(user_games_data["tt_draw_accuracies"])
                )
                > 50,
                (
                    len(user_games_data["win_accuracies"])
                    + len(user_games_data["loss_accuracies"])
                    + len(user_games_data["draw_accuracies"])
                )
                > 50,
            ]
        )
        if enough_games:
            results.append(user_games_data)

    print(json.dumps(summarize_data(results), indent=2))

    get_rating_corr()


if __name__ == "__main__":
    main()
