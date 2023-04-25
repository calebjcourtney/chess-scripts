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
import matplotlib.pyplot as plt


class Player:
    def __init__(self, elo: int):
        self.elo = elo
        self.count = 1

    def update(self, new_elo):
        self.elo = ((self.elo * self.count) + new_elo) / (self.count + 1)
        self.count += 1


elo_pattern = re.compile(r'\[(White|Black)Elo "(\d+)"\]')
username_pattern = re.compile(r'\[(White|Black) "(.+)"\]')
players = dict()

white = None
white_elo = None
black = None
black_elo = None

try:
    for line in tqdm(sys.stdin):
        if line.startswith('[WhiteElo "'):
            white_elo = int(elo_pattern.match(line).group(2))
        elif line.startswith('[BlackElo "'):
            black_elo = int(elo_pattern.match(line).group(2))
        elif line.startswith('[White "'):
            white = username_pattern.match(line).group(2)
        elif line.startswith('[Black "'):
            black = username_pattern.match(line).group(2)

        elif line.startswith("1."):
            if white in players:
                players[white].update(white_elo)
            else:
                players[white] = Player(white_elo)

            if black in players:
                players[black].update(black_elo)
            else:
                players[black] = Player(black_elo)
except KeyboardInterrupt:
    pass

elos = [player.elo for player in players.values()]
plt.hist(elos, bins=25)
plt.show()
