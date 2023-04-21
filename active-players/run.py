"""
This script will take a PGN file
and counts the number of games played at each ELO in the file

The output is a bar graph of number of games played
in each ELO bucket broken into 10 buckets

Output is expectedly a fairly normal distribution
"""

from collections import defaultdict
import sys
import re

from tqdm import tqdm
import matplotlib.pyplot as plt


pattern = re.compile(r'\[(White|Black)Elo "(\d+)"\]')
totals = defaultdict(int)

for line in tqdm(sys.stdin):
    match = pattern.match(line)
    if match:
        totals[match.group(2)] += 1

data = [(int(key), value) for key, value in totals.items()]
data.sort(key=lambda x: x[0])

buckets = []
min_rating = min([int(x) for x, _ in data])
max_rating = max([int(x) for x, _ in data])
val_diff = (max_rating - min_rating) // 10
for rating in range(min_rating, max_rating, val_diff):
    buckets.append((rating, rating + val_diff))

final_data = []
for low, high in buckets:
    temp_data = [
        (rating, count)
        for rating, count in data
        if rating < high
        and rating >= low
    ]
    final_data.append((low, sum(y for _, y in temp_data)))

plt.bar(
    x=[x for x, _ in final_data],
    height=[y for _, y in final_data],
    width=val_diff
)
plt.show()
