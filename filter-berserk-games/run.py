"""
For every game in a pgn (passed in at the command line), output the games where one side berserked
This is only applicable for PGNs generated from the Lichess database: https://database.lichess.org
since that is the only site I'm aware of that allows berserking.

Usage:
cat /path/to/lichess/pgn.pgn | python run.py > berserk_db.pgn
"""
import sys
import re

from chess.pgn import read_game

clock_pattern = re.compile(r"(\d+):(\d+):(\d+)")


def game_is_berserk(game) -> bool:
    event = game.headers.get("Event")
    if event is None or "tournament" not in event:
        return False

    time_control = game.headers["TimeControl"]
    time_control = int(time_control.split("+")[0])

    try:
        white, black = list(game.mainline())[:2]
    except ValueError:
        return False

    for move in [white, black]:
        match = clock_pattern.search(move.comment)
        if not match:
            return False

        hours, minutes, seconds = map(int, [match.group(1), match.group(2), match.group(3)])
        move_tc = hours * 60 * 60 + minutes * 60 + seconds

        if move_tc < time_control:
            return True

    return False


game = read_game(sys.stdin)
count = 0

while game is not None and count < 1000:
    if game_is_berserk(game):
        count += 1
        print(count, file=sys.stderr, end="\r")
        print(f"{game}\n\n")

    game = read_game(sys.stdin)
