

import sys
from collections import defaultdict

import pandas as pd
import chess.pgn


opening_counts = defaultdict(int)
game = chess.pgn.read_game(sys.stdin)
while game is not None:
    opening_counts[game.headers["Opening"]] += 1
    game = chess.pgn.read_game(sys.stdin)


df = pd.DataFrame(
    [
        {
            "Opening": opening,
            "Count": count
        }
        for opening, count in opening_counts.items()
    ]
)

df.sort_values(by="Count", ascending=False, inplace=True)
print(df.head(10))
