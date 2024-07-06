"""
example:
username = "caleb-courtney"
fen = "B1b2rk1/p3ppbp/3p2p1/8/nP3BP1/2PnP2P/1PQ1N3/qNK2R2"
"""

import argparse
import json
from io import StringIO

import requests
import chess
import chess.pgn
from tqdm import tqdm


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


parser = argparse.ArgumentParser()
parser.add_argument("username", type=str)
parser.add_argument("fen", type=str)

args = parser.parse_args()

archives = requests.get(
    f"https://api.chess.com/pub/player/{args.username}/games/archives",
    headers=HEADERS,
).json()["archives"]
archives.sort(reverse=True)


def game_is_match(game: chess.pgn.Game) -> bool:
    assert isinstance(game, chess.pgn.Game)
    board = game.board()
    if board.fen() == args.fen:
        return True

    for move in game.mainline_moves():
        board.push(move)

        if args.fen in board.fen():
            return True

    return False


for url in tqdm(archives):
    data = requests.get(f"{url}", headers=HEADERS).json()
    for game_json in data["games"]:
        if "pgn" not in game_json:
            continue

        game = chess.pgn.read_game(StringIO(game_json["pgn"]))

        if game_is_match(game):
            print(json.dumps(game_json))
            print(url)
