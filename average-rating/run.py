"""
Get the average rating of all the games played in a pgn database
"""
from collections import defaultdict
import sys
import re

from tqdm import tqdm

pattern = re.compile(r'\[(White|Black)Elo "(\d+)"\]')
totals = defaultdict(int)

for line in tqdm(sys.stdin):
    match = pattern.match(line)
    if match:
        totals[int(match.group(2))] += 1

total = sum(key * value for key, value in totals.items())
games = sum(value for key, value in totals.items())

average = total / games
print(average)
