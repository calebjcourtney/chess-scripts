import sys
import json
from collections import defaultdict

total = defaultdict(int)
for line in sys.stdin:
    start_json = line.index(r"{")

    data = json.loads(line[start_json:])
    if data.get("title") is None:
        total[data["status"]] += 1

print(total)
