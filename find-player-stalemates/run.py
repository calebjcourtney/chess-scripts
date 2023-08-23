"""
example:
username = "caleb-courtney"
"""

import argparse

from io import StringIO

import requests
import chess
import chess.pgn
from tqdm import tqdm

import warnings
warnings.filterwarnings("ignore")


parser = argparse.ArgumentParser()
parser.add_argument("username", type=str)

args = parser.parse_args()

archives = requests.get(
    f"https://api.chess.com/pub/player/{args.username}/games/archives",
    verify=False
).json()["archives"]
archives.sort()


def white_stalemated(game: chess.pgn.Game) -> bool:
    # returns true if white made the last move
    assert isinstance(game, chess.pgn.Game)
    return len(list(game.mainline_moves())) % 2 == 1


for url in tqdm(archives):
    data = requests.get(url).json()
    for game_json in data["games"]:
        if "pgn" not in game_json:
            continue

        if game_json["white"]["result"] != "stalemate":
            continue

        game = chess.pgn.read_game(StringIO(game_json["pgn"]))
        result = white_stalemated(game)

        if (args.username == game_json["white"]["username"] and result) or (args.username == game_json["black"]["username"] and not result):
            print(game.headers.get("Link"))
