from typing import NamedTuple
from datetime import datetime
from pathlib import Path
import json

import requests


def expected_score(opponent_ratings: list[float], own_rating: float) -> float:
    """How many points we expect to score in games with these opponents"""
    return sum(
        1 / (1 + 10 ** ((opponent_rating - own_rating) / 400))
        for opponent_rating in opponent_ratings
    )


def performance_rating(opponent_ratings: list[float], score: float) -> int:
    """Calculate mathematically perfect performance rating with binary search."""
    if score == len(opponent_ratings):
        return sum(opponent_ratings) / len(opponent_ratings) + 800
    elif score == 0:
        return max(100, min(opponent_ratings) - 400)

    lo, hi = 0, 10000

    while hi - lo > 0.0001:
        mid = (lo + hi) / 2

        if expected_score(opponent_ratings, mid) < score:
            lo = mid
        else:
            hi = mid

    return round(mid)


def main():
    opponent_ratings = [
        293,
        1786,
        1186,
        1100,
        1897,
    ]
    print(sum(opponent_ratings) / len(opponent_ratings))

    im_perf = 2450
    gm_perf = 2600

    score = 4.0
    perf = performance_rating(opponent_ratings, score)
    print(perf)
    print(f"expected score: {expected_score(opponent_ratings, 1558)}")


if __name__ == "__main__":
    main()
