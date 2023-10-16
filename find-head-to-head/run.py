import argparse
from io import StringIO

import requests
from tqdm import tqdm
import chess.pgn


def get_data(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    }

    response = requests.request("GET", url, headers=headers)

    return response.json()


def get_month_overlap(user_1_archives: list[str], user_2_archives: list[str]) -> list[str]:
    user_1_months = set()
    for url in user_1_archives:
        year, month = url.split("/")[-2:]
        user_1_months.add(f"{year}/{month}")

    overlap_months = set()
    for url in user_2_archives:
        if is_valid_month(user_1_months, url):
            overlap_months.add(url)

    return overlap_months


def is_valid_month(month_overlaps: set[str], archive_url: str) -> bool:
    for month_overlap in month_overlaps:
        if month_overlap in archive_url:
            return True

    return False


def main(user1, user2):
    game_results = {
        "bullet": {
            "wins": 0,
            "losses": 0,
            "draws": 0
        },
        "blitz": {
            "wins": 0,
            "losses": 0,
            "draws": 0
        },
        "rapid": {
            "wins": 0,
            "losses": 0,
            "draws": 0
        }
    }
    user_1_archives = get_data(f"https://api.chess.com/pub/player/{user1}/games/archives")["archives"]
    user_2_archives = get_data(f"https://api.chess.com/pub/player/{user2}/games/archives")["archives"]
    month_overlap = get_month_overlap(user_1_archives, user_2_archives)

    players = {user1, user2}

    for url in tqdm(month_overlap):
        archive_response = get_data(url)
        for game_json in archive_response["games"]:
            # not a rated game
            if (
                not game_json["rated"]
                or game_json["rules"] != "chess"
                or game_json["initial_setup"] != "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
                or "pgn" not in game_json
            ):
                continue

            white = game_json["white"]["username"]
            black = game_json["black"]["username"]

            if {white, black} != players:
                continue

            time_class = game_json["time_class"]

            game = chess.pgn.read_game(StringIO(game_json["pgn"]))
            result = game.headers["Result"]
            if result == "1/2-1/2":
                game_results[time_class]["draws"] += 1
            elif result == "1-0" and white == user1 or result == "0-1" and black == user1:
                game_results[time_class]["wins"] += 1
            else:
                game_results[time_class]["losses"] += 1

    print(game_results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("user1", help="The username of the player to find head-to-head games for.")
    parser.add_argument("user2", help="The username of the player to find head-to-head games for.")
    args = parser.parse_args()

    main(args.user1, args.user2)
