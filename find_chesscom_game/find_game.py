"""
example:
username = "caleb-courtney"
fen = "B1b2rk1/p3ppbp/3p2p1/8/nP3BP1/2PnP2P/1PQ1N3/qNK2R2"
"""

import argparse

from io import StringIO

import requests
import chess
import chess.pgn
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("username", type=str)
parser.add_argument("fen", type=str)

args = parser.parse_args()

archives = requests.get(
    f"https://api.chess.com/pub/player/{args.username}/games/archives",
    verify=False
).json()["archives"]
archives.sort(reverse=True)


def game_is_match(game: chess.pgn.Game) -> bool:
    assert isinstance(game, chess.pgn.Game)
    board = chess.Board()
    if board.fen() == args.fen:
        return True

    for move in game.mainline_moves():
        board.push(move)

        if args.fen in board.fen():
            return True

    return False


for url in tqdm(archives):
    pgn_response = requests.get(f"{url}/pgn", verify=False)

    pgn = StringIO(pgn_response.text)

    game = chess.pgn.read_game(pgn)

    while game is not None and not game_is_match(game):
        game = chess.pgn.read_game(pgn)

    if game is not None and game_is_match(game):
        break

print(game.headers.get("Link"))
