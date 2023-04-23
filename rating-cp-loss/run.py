"""
Reads in a pgn and estimates the average loss per move for each rating.
Assumes that the pgn is in a format consistent with lichess db formats
Additionally, does not take into account mate in X moves as part of quantity
"""
from collections import defaultdict
import re
import sys

import matplotlib.pyplot as plt
import numpy as np


class EloLoss:
    def __init__(self, elo: int, loss: float):
        self.elo: int = elo
        self.loss: float = loss


extract_elo = re.compile(r'\[(White|Black)Elo "(\d+)"\]')
extract_eval = re.compile(r'%eval ((\d+\.\d+)|(#\d+))')

elo_loss_count = defaultdict(lambda: defaultdict(int))
game_count = 0

try:
    white_elo = None
    black_elo = None
    for line in sys.stdin:
        if line.startswith("[WhiteElo"):
            white_elo = int(extract_elo.search(line).group(2))
        elif line.startswith("[BlackElo"):
            black_elo = int(extract_elo.search(line).group(2))
        elif line.startswith("1."):
            game_count += 1
            if game_count % 100000 == 0:
                print(game_count, file=sys.stderr, end="\r")
            result = extract_eval.findall(line)
            for i, (prior, current) in enumerate(zip(result, result[1:])):
                if "#" in current[0] or "#" in prior[0]:
                    continue

                elo = black_elo if i % 2 == 0 else white_elo

                elo_loss_count[elo][abs(round(float(current[0]) - float(prior[0]), 2))] += 1

            white_elo = None
            black_elo = None
except KeyboardInterrupt:
    pass

elo_losses = []

for rating, loss_counts in elo_loss_count.items():
    cp_losses = 0
    for loss, count in loss_counts.items():
        cp_losses += loss * count

    elo_losses.append(
        EloLoss(
            rating,
            cp_losses / sum(count for _, count in loss_counts.items())
        )
    )


slope, intercept = np.polyfit([x.elo for x in elo_losses], [x.loss for x in elo_losses], 1)
y_fit = [x.elo * slope + intercept for x in elo_losses]

plt.scatter(
    x=[record.elo for record in elo_losses],
    y=[record.loss for record in elo_losses]
)
plt.plot([record.elo for record in elo_losses], y_fit, color="red")
plt.show()
