import argparse
from collections import defaultdict
from io import StringIO
import time

import requests
from tqdm import tqdm

import chess
import chess.pgn

import warnings
warnings.filterwarnings("ignore")

HEADERS = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}


def read_game(pgn: StringIO):
    try:
        game = chess.pgn.read_game(pgn)
    except AssertionError:
        return read_game()

    return game


def get_largest_moves_position(game: chess.pgn.Game, remainder: int):
    moves = 0
    position = None
    board = game.board()
    for i, move in enumerate(list(game.mainline_moves())):
        board.push(move)

        if i % 2 == remainder:
            c = board.legal_moves.count()
            if c > moves:
                moves = c
                position = board.fen()

    return moves, position


def main(username):
    largest_moves = 0
    largest_option_json = None
    largest_position = None

    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    archives = requests.get(
        url,
        headers=HEADERS
    )
    try:
        archives = archives.json()["archives"]
    except Exception:
        print(archives.text)
        print(archives.url)
    archives.sort()

    for url in tqdm(archives):
        archive_response = requests.get(f"{url}", headers=HEADERS)
        if "games" not in archive_response.json():
            print(f"could not find games in json for {url}")
            print(archive_response.json())
            continue

        for game_json in archive_response.json()["games"]:
            # if the initial setup isn't a usual game of chess
            if game_json["initial_setup"] != "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1":
                continue

            if "pgn" not in game_json:
                continue

            remainder = 0 if username == game_json["white"]["username"] else 1

            pgn = StringIO(game_json["pgn"])
            game = read_game(pgn)

            if game.headers.get("Variant"):
                continue

            moves, position = get_largest_moves_position(game, remainder)

            if moves > largest_moves:
                largest_moves = moves
                largest_option_json = game_json
                largest_position = position

        time.sleep(0.5)

    print(largest_moves)
    print(largest_option_json)
    print(largest_position)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("chesscom_username", type=str, help="your chess.com username")

    args = parser.parse_args()

    main(args.chesscom_username)
