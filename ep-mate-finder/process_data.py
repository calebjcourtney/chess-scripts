import sys
from typing import Tuple, List
import re

import time

MOVETEXT_REGEX = re.compile(r"([NBRQK])?([a-h])?([1-8])?(x)?([a-h][1-8])(=[NBRQK])?(\+|#)?|O-O(-O)?(\+|#)?")


files = "abcdefgh"
ranks = "{}x{}3#", "{}x{}6#"

ep_mate_moves = set()
for rank in ranks:
    for f1, f2 in zip(files, files[1:]):
        ep_mate_moves.add(rank.format(f1, f2))
        ep_mate_moves.add(rank.format(f2, f1))

setup_moves = set()
for rank in "45":
    for file in files:
        setup_moves.add(f"{file}{rank}")


class Game:
    headers: dict = {}
    moves: str = ""

    def __str__(self) -> str:
        output = ""
        for key, value in self.headers.items():
            output += f'[{key} "{value}"]\n'

        output += f"\n{self.moves}\n"

        return output

    def __repr__(self):
        return self.__str__()


def is_header_row(row: str) -> bool:
    return row.startswith("[")


def parse_header(header_row: str) -> Tuple[str, str]:
    header_row = header_row.strip("[")
    header_row = header_row.strip("]")

    key = header_row.split()[0]
    value = " ".join(header_row.split()[1:]).strip('"')

    return key, value


def is_move_row(row: str) -> bool:
    return row.startswith("1. ")


def parse_moves(row: str) -> List[str]:
    return [x.group(0) for x in re.finditer(MOVETEXT_REGEX, row)]


def is_ep_mate(move_row: str) -> bool:
    moves = parse_moves(move_row)
    return len(moves) > 10 and moves[-2] in setup_moves and moves[-1] in ep_mate_moves


game = Game()

start_time = time.time()
game_count = 0

for row in sys.stdin:
    row = row.strip()
    if is_header_row(row):
        key, value = parse_header(row)
        game.headers[key] = value

    elif is_move_row(row):
        game_count += 1
        game.moves = row
        if is_ep_mate(row):
            print(game)

        if game_count % 10000 == 0:
            print(
                f"{game_count} ({round(game_count / (time.time() - start_time))} g/s)",
                file = sys.stderr,
                end = "\r"
            )

        game = Game()
