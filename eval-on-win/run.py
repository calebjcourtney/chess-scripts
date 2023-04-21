"""
For wins/losses/draws, get the average evaluation for each result in a PGN database

Only uses moves after move 10 (5 for each player) to avoid including eval from opening theory

Does not include mate in X evaluations
"""
from collections import defaultdict
import sys
import re

from tqdm import tqdm

pattern = re.compile(r'\[%eval (-?\d+.\d+)\]')
totals = defaultdict(int)

white_evals = []
black_evals = []
draw_evals = []

for line in tqdm(sys.stdin):
    if r'%eval' not in line:
        continue

    matches = pattern.findall(line)
    if len(matches) < 11:
        continue

    matches = matches[10:]

    if matches:
        avg = sum(map(float, matches)) / len(matches)

        if '1/2-1/2' in line:
            draw_evals.append(avg)

        elif '1-0' in line:
            white_evals.append(avg)

        elif '0-1' in line:
            black_evals.append(avg)

print('White:', round(sum(white_evals) / len(white_evals), 2))
print('Black:', round(sum(black_evals) / len(black_evals), 2))
print('Draws:', round(sum(draw_evals) / len(draw_evals), 2))
