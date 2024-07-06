import argparse

import requests
from tqdm import tqdm


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


def main(user_1: str, user_2: str):
    url = f"https://api.chess.com/pub/player/{user_1}/games/archives"
    archives = requests.get(url, headers=HEADERS).json()["archives"]

    output = {
        "win": 0,
        "loss": 0,
        "draw": 0,
    }

    for url in tqdm(archives):
        games = requests.get(url, headers=HEADERS).json()["games"]

        for game in games:
            if {
                game["white"]["username"].lower(),
                game["black"]["username"].lower(),
            } != {user_1, user_2}:
                continue

            if game["time_class"] != "blitz":
                continue

            if game["white"]["username"].lower() == user_1 and game["white"]["result"] == "win":
                output["win"] += 1
            elif game["black"]["username"].lower() == user_1 and game["black"]["result"] == "black":
                output["win"] += 1
            elif game["white"]["username"].lower() == user_2 and game["white"]["result"] == "win":
                output["loss"] += 1
            elif game["black"]["username"].lower() == user_2 and game["black"]["result"] == "black":
                output["loss"] += 1
            else:
                output["draw"] += 1

    print(output)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "user_1",
        type=str,
        help="The first user to compare",
    )
    argument_parser.add_argument(
        "user_2",
        type=str,
        help="The second user to compare",
    )
    args = argument_parser.parse_args()
    main(args.user_1.lower(), args.user_2.lower())
