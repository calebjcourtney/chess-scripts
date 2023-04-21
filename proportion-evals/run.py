"""
For wins/losses/draws, get the average evaluation for each result in a PGN database
Does not include mate in X evaluations
"""
import sys
from tqdm import tqdm

games = 0
eval_games = 0

for line in tqdm(sys.stdin):
    if line.startswith("1."):
        games += 1

    else:
        continue

    if r"[%eval " in line:
        eval_games += 1

    if r'%eval' not in line:
        continue

print(f"Total games: {games}")
print(f"Games with eval: {eval_games}")
print(f"Proportion: {round(eval_games / games, 2)}")
