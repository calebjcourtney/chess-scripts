import argparse
from collections import defaultdict
from io import StringIO

import requests
from tqdm import tqdm

import chess
import chess.pgn
import chess.engine

import warnings
warnings.filterwarnings("ignore")


def read_game(pgn: StringIO):
    try:
        game = chess.pgn.read_game(pgn)
    except AssertionError:
        return read_game()

    return game


def get_game_positions(game: chess.pgn.Game, remainder: int):
    output = []
    board = game.board()
    for i, move in enumerate(list(game.mainline_moves())[:30]):
        board.push(move)
        if i % 2 == remainder:
            output.append(board.fen())

    return output


def main(username, engine_path):
    position_counts = defaultdict(int)
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    archives = requests.get(
        url,
        headers={'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
    )
    try:
        archives = archives.json()["archives"]
    except Exception:
        print(archives.text)
        print(archives.url)
    archives.sort()

    for url in tqdm(archives):
        archive_response = requests.get(f"{url}")
        for game_json in archive_response.json()["games"]:
            # not a rated game
            if not game_json["rated"]:
                continue

            # bullet game
            if game_json["time_class"] == "bullet":
                continue

            # if the initial setup isn't a usual game of chess
            if game_json["initial_setup"] != "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1":
                continue

            if "pgn" not in game_json:
                continue

            remainder = 0 if username == game_json["white"]["username"] else 1

            pgn = StringIO(game_json["pgn"])
            game = read_game(pgn)

            for position in get_game_positions(game, remainder):
                position_counts[position] += 1

            game = read_game(pgn)

    position_counts = {key: value for key, value in position_counts.items() if value >= 5}

    for position in tqdm(position_counts.keys()):
        board = chess.Board(position)
        info = engine.analyse(board, chess.engine.Limit(depth=10))

        try:
            if info["score"].relative.cp > 100:
                print(position)
                print(position_counts[position])
        except Exception:
            pass

    engine.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--chesscom_username", type=str, help="your chess.com username", default=None)
    parser.add_argument("--file_path", type=str, help="path to source file to analyze moves", default=None)
    parser.add_argument("--engine", type=str, default="/usr/local/bin/stockfish", help="path to your stockfish uci engine")

    args = parser.parse_args()

    assert args.chesscom_username is not None or args.file_path is not None

    main(args.chesscom_username, args.engine)
