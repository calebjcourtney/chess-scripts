from typing import NamedTuple
from datetime import datetime
from pathlib import Path
import json

import requests
import pandas as pd
import matplotlib.pyplot as plt


def expected_score(opponent_ratings: list[float], own_rating: float) -> float:
    """How many points we expect to score in games with these opponents"""
    return sum(
        1 / (1 + 10 ** ((opponent_rating - own_rating) / 400))
        for opponent_rating in opponent_ratings
    )


def performance_rating(opponent_ratings: list[float], score: float) -> int:
    """Calculate mathematically perfect performance rating with binary search."""
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
        2325,
        2351,
        2452,
        2406,
        2368,
        2474,
        2388,
        2400,
        2304,
    ]
    print(sum(opponent_ratings) / len(opponent_ratings))

    im_perf = 2450
    gm_perf = 2600

    score = 0.5
    while score < len(opponent_ratings):
        perf = performance_rating(opponent_ratings, score)
        if perf >= gm_perf:
            print(f"Score: {score}, Performance: {perf}")
            break

        score += 0.5


if __name__ == "__main__":
    main()
