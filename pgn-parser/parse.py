"""
This script provides easy parsing of large chess pgn's
Please note this is along the lines of what can be done with the python-chess library,
but this parser is faster because it's doing less work, like move validation.

With shortcuts like this, we get much faster performance, with some tests close to 1500 games/sec
"""
import sys
from typing import List, Dict, Tuple
import json
import re
from datetime import datetime


from chess.pgn import (
    CLOCK_REGEX,
    EVAL_REGEX
)

MOVETEXT_REGEX = re.compile(r"([NBRQK])?([a-h])?([1-8])?(x)?([a-h][1-8])(=[NBRQK])?(\+|#)?|O-O(-O)?")


class Move:
    san: str = ""
    time: str = ""
    color: str = ""
    evaluation: float = None

    def __repr__(self) -> str:
        return f"<Move(san={self.san}, time={self.time}, color={self.color}, evaluation={self.evaluation})>"

    def __dict__(self) -> Dict[str, str]:
        return {
            "san": self.san,
            "time": self.time,
            "color": self.color,
            "evaluation": self.evaluation
        }


class Game:
    headers: Dict[str, str] = dict()
    moves: List[Move] = []

    def __repr__(self):
        return json.dumps({"moves": str(self.moves), "headers": str(self.headers)})

    def to_json(self):
        return json.dumps(
            {
                "moves": [move.__dict__() for move in self.moves],
                "headers": self.headers
            }
        )


def is_header(row: str) -> bool:
    return row.startswith("[") and row.endswith("]")


def parse_header(row: str) -> Tuple[str, str]:
    """Summary

    Args:
        row (TYPE): Description

    Returns:
        TYPE: Description
    """
    row = row.lstrip("[")
    row = row.rstrip("]")
    key, value = row.split(' "')
    value = value.strip('"')

    return key, value


def is_moves(row: str) -> bool:
    return row.startswith("1.")


def parse_moves(row: str) -> List[Move]:
    sans = list(MOVETEXT_REGEX.finditer(row))
    clocks = list(CLOCK_REGEX.finditer(row))

    # if there are no clock times, we're not going to bother parsing the moves
    if not clocks:
        return []

    assert len(sans) == len(clocks)
    evals = list(EVAL_REGEX.finditer(row))

    moves = []
    color = "white"
    for index in range(len(sans)):
        move = Move()
        move.san = sans[index].group(0)
        move.time = clocks[index].group(0).split()[1].strip("]")

        move.color = color
        color = "black" if color == "white" else "white"

        if evals and index < len(evals):
            assert len(evals) >= len(clocks) - 1, f"{len(evals)} != {len(clocks)}"
            move.evaluation = evals[index].group(0).split()[1].strip("]")

        moves.append(move)

    return moves


def read_game(file) -> Game:
    """
    Takes a file object and reads the next game from the file.

    Returns:
        Game: The next game in the file
    """
    game = Game()
    for row in file:
        row = row.strip()
        if is_header(row):
            key, value = parse_header(row)
            game.headers[key] = value

        elif is_moves(row):
            game.moves = parse_moves(row)
            break

    return game


if __name__ == '__main__':
    in_file = sys.stdin
    count = 0
    start = datetime.utcnow()
    while in_file:
        game = read_game(in_file)
        count += 1
        if count % 10000 == 0:
            print(f"{count} ({round(count / (datetime.utcnow() - start).seconds, 0)} games/sec)", end="\r")
