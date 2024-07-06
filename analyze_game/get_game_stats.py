import json
from io import StringIO
import re

import chess.pgn
import chess.engine
import chess

from statistics import pstdev as stdev
from statistics import median


clock_pattern = re.compile(r"\d+:\d+:\d+(\.\d+)?")


def get_clock_in_seconds(node_comment):
    time_on_clock = clock_pattern.search(node_comment)
    hours, minutes, seconds = map(float, time_on_clock.group().split(":"))
    return hours * 60 * 60 + minutes * 60 + seconds * 60


def clock_diffs(clock_times):
    return [
        x - y
        for x, y in zip(clock_times, clock_times[1:])
    ]


def get_game_stats(game, engine_path="/usr/local/bin/stockfish"):
    board = chess.Board()

    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    current_eval = int(engine.analyse(board, chess.engine.Limit(time=0.2))["score"].white().score(mate_score=100000))
    white_clock_times = []
    white_cp_loss = []
    black_clock_times = []
    black_cp_loss = []
    for color, node in enumerate(game.mainline()):
        print(("white" if color % 2 == 0 else "black"), node.move)
        seconds = get_clock_in_seconds(node.comment)
        board.push(node.move)
        new_eval = int(engine.analyse(board, chess.engine.Limit(time=0.2))["score"].white().score(mate_score=100000))

        if color % 2 == 0:
            white_clock_times.append(seconds)
            white_cp_loss.append(current_eval - new_eval)
        else:
            black_clock_times.append(seconds)
            black_cp_loss.append(current_eval - new_eval)

    engine.close()

    white_clock_diffs = clock_diffs(white_clock_times)
    black_clock_diffs = clock_diffs(black_clock_times)

    white_cp_loss = list(filter(lambda x: x < 10000, white_cp_loss))
    black_cp_loss = list(filter(lambda x: x < 10000, black_cp_loss))

    stats = {
        "white_move_times": {
            "avg": sum(white_clock_diffs) / len(white_clock_diffs),
            "median": median(white_clock_diffs),
            "stdev": stdev(white_clock_diffs),
        },
        "black_move_times": {
            "avg": sum(black_clock_diffs) / len(black_clock_diffs),
            "median": median(black_clock_diffs),
            "stdev": stdev(black_clock_diffs),
        },
        "white_cp_loss": {
            "avg": sum(white_cp_loss) / len(white_cp_loss),
            "median": median(white_cp_loss),
            "stdev": stdev(white_cp_loss),
        },
        "black_cp_loss": {
            "avg": sum(black_cp_loss) / len(black_cp_loss),
            "median": median(black_cp_loss),
            "stdev": stdev(black_cp_loss),
        },
    }

    return stats


data = json.load(open("jan_hikaru.json", 'r'))

for game in data["games"]:
    pgn = chess.pgn.read_game(StringIO(game["pgn"]))
    stats = get_game_stats(pgn)
    print(stats)
