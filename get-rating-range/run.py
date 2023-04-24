"""
This script will take a PGN file
and counts the number of games played at each ELO in the file

The output is a bar graph of number of games played
in each ELO bucket broken into 10 buckets

Output is expectedly a fairly normal distribution
"""

import sys
import re

from tqdm import tqdm


elo_pattern = re.compile(r'\[(White|Black)Elo "(\d+)"\]')

min_elo = 1_000_000
max_elo = -1

try:
    for line in tqdm(sys.stdin):
        if line.startswith('[WhiteElo "'):
            white_elo = int(elo_pattern.match(line).group(2))
            min_elo = min(min_elo, white_elo)
            max_elo = max(max_elo, white_elo)

        elif line.startswith('[BlackElo "'):
            black_elo = int(elo_pattern.match(line).group(2))
            min_elo = min(min_elo, white_elo)
            max_elo = max(max_elo, white_elo)

except KeyboardInterrupt:
    pass

print(f"Min ELO: {min_elo}")
print(f"Max ELO: {max_elo}")
