"""
This script will read a PGN file passed in from the command line
and gets the max, min, and average ELO of the players that played that month
"""

import sys
import re

from tqdm import tqdm


elo_pattern = re.compile(r'\[(White|Black)Elo "(\d+)"\]')

min_elo = 1_000_000
max_elo = -1
avg_elo = 0
count = 0

for line in tqdm(sys.stdin):
    if line.startswith('[WhiteElo "'):
        white_elo = int(elo_pattern.match(line).group(2))
        min_elo = min(min_elo, white_elo)
        max_elo = max(max_elo, white_elo)
        avg_elo = ((avg_elo * (1 if count == 0 else count)) + white_elo) / (count + 1)
        count += 1

    elif line.startswith('[BlackElo "'):
        black_elo = int(elo_pattern.match(line).group(2))
        min_elo = min(min_elo, white_elo)
        max_elo = max(max_elo, white_elo)
        avg_elo = ((avg_elo * (1 if count == 0 else count)) + black_elo) / (count + 1)
        count += 1


print(f"Min ELO: {min_elo}")
print(f"Max ELO: {max_elo}")
print(f"Avg ELO: {round(avg_elo)}")
