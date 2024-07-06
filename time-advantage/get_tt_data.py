import re
from io import StringIO
import sys

import requests
from chess.pgn import read_game
from tqdm import tqdm


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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# https://www.chess.com/tournament/live/late-titled-tuesday-blitz-march-05-2024-4605130
TT_RE_MATCH = re.compile(r"^.*(late|early)-titled-tuesday-blitz-.*-2024-\d+")
CLOCK_PATTERN = re.compile(
    r"(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+(?:\.\d+)?)"
)

TT_URLS = {
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-february-06-2024-4547612",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-february-20-2024-4576498",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-january-23-2024-4518064",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-march-19-2024-4634461",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-march-19-2024-4634462",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-february-13-2024-4576494",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-march-12-2024-4619545",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-march-05-2024-4605130",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-march-26-2024-4648836",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-january-16-2024-4503498",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-march-26-2024-4648835",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-january-16-2024-4503497",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-january-09-2024-4490239",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-january-02-2024-4490237",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-january-23-2024-4518065",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-january-30-2024-4532494",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-february-13-2024-4576493",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-february-06-2024-4547611",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-february-20-2024-4576499",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-january-09-2024-4490240",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-february-27-2024-4590817",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-february-27-2024-4590818",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-january-30-2024-4532496",
    "https://api.chess.com/pub/tournament/late-titled-tuesday-blitz-january-02-2024-4490238",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-march-05-2024-4605129",
    "https://api.chess.com/pub/tournament/early-titled-tuesday-blitz-march-12-2024-4619544",
}


def get_blitz_leaderboard():
    url = "https://api.chess.com/pub/leaderboards"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    blitz_leaderboard = data["live_blitz"]
    return [user["username"] for user in blitz_leaderboard]


def get_tt_tournament_links(usernames):
    for user in tqdm(usernames):
        url = f"https://api.chess.com/pub/player/{user}/tournaments"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        for tournament in data["finished"]:
            if TT_RE_MATCH.match(tournament["@id"]):
                yield tournament["@id"]


def get_tt_data():
    # needs a pandas dataframe with output of white_seconds_left, black_seconds_left, result
    # result can be 1 for white win, 0 for draw, -1 for black win
    global TT_URLS

    if TT_URLS is None:
        usernames = get_blitz_leaderboard()
        TT_URLS = set(get_tt_tournament_links(usernames))

        print(TT_URLS, file=sys.stderr)

    for url in tqdm(TT_URLS):
        response = requests.get(f"{url}/11/1", headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        for game in data["games"]:
            white_seconds = 180
            black_seconds = 180
            pgn_game = read_game(StringIO(game["pgn"]))
            result = 0.0
            if pgn_game.headers["Result"] == "1-0":
                result = 1.0
            elif pgn_game.headers["Result"] == "0-1":
                result = -1.0

            for index, node in enumerate(pgn_game.mainline()):
                clock_time = str(node.comment)
                hours, minutes, seconds = CLOCK_PATTERN.search(clock_time).groups()

                if index % 2 == 0:
                    white_seconds = (
                        int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                    )
                else:
                    black_seconds = (
                        int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                    )

                yield white_seconds, black_seconds, result


if __name__ == "__main__":
    print("white_seconds,black_seconds,result")
    for white_seconds, black_seconds, result in get_tt_data():
        print(f"{white_seconds},{black_seconds},{result}")
