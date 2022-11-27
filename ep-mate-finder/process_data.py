import sys

import time

import chess.pgn


files = "abcdefgh"
ranks = "{}x{}3#", "{}x{}6#"

ep_mate_moves = set()
for rank in ranks:
    for f1, f2 in zip(files, files[1:]):
        ep_mate_moves.add(rank.format(f1, f2))
        ep_mate_moves.add(rank.format(f2, f1))

previous_moves = set()
for rank in "45":
    for file in files:
        previous_moves.add(f"{file}{rank}")


def is_ep_mate(game) -> bool:
    moves = list(game.mainline_moves())
    return len(moves) > 10 and moves[-2] in previous_moves and moves[-1] in ep_mate_moves


game = chess.pgn.read_game(sys.stdin)

start_time = time.time()
game_count = 0

while game is not None:
    if is_ep_mate(game):
        print(game)
        print("\n\n")

    game = chess.pgn.read_game(sys.stdin)
