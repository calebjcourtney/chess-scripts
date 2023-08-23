"""
Reads in a pgn and estimates the average loss per move for each rating.
Assumes that the pgn is in a format consistent with lichess db formats
Only looks at ELO ranges 800-2500
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
extract_tc = re.compile(r'\[TimeControl "(\d+)\+(\d+)"')

elo_loss_count = defaultdict(lambda: defaultdict(int))
game_count = 0

try:
    white_elo = None
    black_elo = None
    time_control = None
    for line in sys.stdin:
        if line.startswith("[TimeControl") and '[TimeControl "-"]' not in line:
            tc_match = extract_tc.search(line)
            if tc_match is None:
                continue

            seconds = int(tc_match.group(1))
            increment = int(tc_match.group(2))
            if seconds + 40 * increment > 179:
                time_control = "slow"
            else:
                time_control = "fast"

        if line.startswith("[WhiteElo"):
            white_elo = int(extract_elo.search(line).group(2))
        elif line.startswith("[BlackElo"):
            black_elo = int(extract_elo.search(line).group(2))
        elif (
            line.startswith("1.")
            and time_control == "slow"
            and (800 < white_elo < 2500)
            and (800 < black_elo < 2500)
        ):
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

elo_losses = {}

for rating, loss_counts in elo_loss_count.items():
    cp_losses = 0
    for loss, count in loss_counts.items():
        cp_losses += loss * count

    elo_losses[rating] = cp_losses / sum(loss_counts.values())


smoothed_line = []
for x in range(800, 2500):
    smoothed_line.append(
        sum({count for elo, count in elo_losses.items() if elo > x - 100 and elo < x + 100})
        / max(1, len({count for elo, count in elo_losses.items() if elo > x - 100 and elo < x + 100}))
    )


slope, intercept = np.polyfit([x.elo for x in elo_losses], [x.loss for x in elo_losses], 1)
print(f"y = {slope}x + {intercept}")
y_fit = [(elo, elo * slope + intercept) for elo in elo_losses.keys()]

plt.scatter(
    x=[record[0] for record in elo_losses],
    y=[record[1] for record in elo_losses]
)
plt.plot([record.elo for record in elo_losses], y_fit, color="red")
plt.plot(list(range(800, 2500)), smoothed_line, color="green")
plt.show()
