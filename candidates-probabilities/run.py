"""
Given a list of players and their ratings, iterate through pairings and possible outcomes.
Use the Elo ratings to determine probabilities of each result.
Determine overall probability of each player winning the tournament.

Example:
    players = [
        Player('A', 1600),
        Player('B', 1400),
        Player('C', 1200),
        Player('D', 1000)
    ]
    tournament = Tournament(players)
    tournament.run()
    print(tournament.results)
    # {'A': 0.5, 'B': 0.25, 'C': 0.15, 'D': 0.1}
"""

from typing import List, Dict
from typing import NamedTuple
import json
import random
from functools import lru_cache
from collections import defaultdict

from chess.pgn import read_headers
import pandas as pd


class Player(NamedTuple):
    name: str
    rating: int

    def __repr__(self):
        return json.dumps({"name": self.name, "rating": self.rating})

    def __hash__(self):
        return tuple([self.name, self.rating]).__hash__()


class Pairing(NamedTuple):
    p1: Player
    p2: Player

    @lru_cache
    def calculate_outcome_probability(self) -> tuple[float, float, float]:
        """
        Calculate the probability of win, draw, and loss between two players based on their Elo ratings.

        Returns:
        tuple: A tuple containing the probabilities of win, draw, and loss for player 1.
        """
        # Calculate the expected score for player 1
        expected_score_player1 = 1 / (
            1 + 10 ** ((self.p2.rating - self.p1.rating) / 400)
        )

        # Calculate the probabilities of win, draw, and loss for player 1
        win_probability = expected_score_player1
        draw_probability = 1 - abs(0.5 - expected_score_player1)
        loss_probability = 1 - expected_score_player1

        return (
            win_probability / (win_probability + draw_probability + loss_probability),
            draw_probability / (win_probability + draw_probability + loss_probability),
            loss_probability / (win_probability + draw_probability + loss_probability),
        )


class Outcome:
    def __init__(self, results: dict[Player, float], probability: float):
        self.results = results
        self.probability = probability

    def update(self, results: dict[Player, float], prob: float):
        self.results.update(results)
        self.probability *= prob

    def copy(self):
        return Outcome(self.results, self.probability)

    def __repr__(self):
        return json.dumps(
            {
                "results": {
                    player.name: score for player, score in self.results.items()
                },
                "probability": self.probability,
            }
        )

    def __eq__(self, other):
        return self.results == other.results

    def __hash__(self):
        return (tuple(self.results.items())).__hash__()


class Tournament:
    def __init__(
        self,
        standings: Outcome,
        pairings: List[Pairing] | None = None,
    ):
        self.results = standings
        self.pairings = pairings

    def get_all_pairings(self) -> list[Outcome]:
        outcomes: list[Outcome] = [self.results]
        for pairing in self.pairings:
            new_outcomes: list[Outcome] = []
            w, d, l = pairing.calculate_outcome_probability()
            for prob, score in zip([w, d, l], [1, 0.5, 0]):
                for outcome in outcomes:
                    temp_res = {key: value for key, value in outcome.results.items()}
                    temp_res[pairing.p1] += score
                    temp_res[pairing.p2] += 1 - score
                    new_outcomes.append(Outcome(temp_res, prob * outcome.probability))

            outcomes = new_outcomes[:]

        return group_outcomes(outcomes)

    def simulate(self, benchmark) -> list[Outcome]:
        output: list[Outcome] = []
        for _ in range(benchmark):
            results = defaultdict(float)
            for key, value in self.results.results.items():
                results[key] = value
            for pairing in self.pairings:
                w, d, l = pairing.calculate_outcome_probability()
                outcome = random.uniform(0.0, 1.0)
                if outcome < l:
                    results[pairing.p2] += 1
                elif outcome < l + d:
                    results[pairing.p1] += 0.5
                    results[pairing.p2] += 0.5
                else:
                    results[pairing.p1] += 1

            output.append(Outcome(results, 1 / benchmark))

        return group_outcomes(output)

    def run(self):
        benchmark = min(3 ** len(self.pairings), 50000)
        if benchmark < 50000:
            print(f"Running all pairings.")
            outcomes = self.get_all_pairings()
        else:
            print(f"Running {benchmark} simulations.")
            outcomes = self.simulate(benchmark)

        return outcomes


def solo_win_probabilities(outcomes: list[Outcome]):
    print("Probabilties of number of finalists")
    solo_win = 0.0
    two_win = 0.0
    three_win = 0.0
    four_win = 0.0
    other_outcome = 0.0

    for outcome in outcomes:
        max_score = max(outcome.results.values())
        num_max_scores = len([x for x in outcome.results.values() if x == max_score])
        if num_max_scores == 4:
            four_win += outcome.probability
        elif num_max_scores == 3:
            three_win += outcome.probability
        elif num_max_scores == 2:
            two_win += outcome.probability
        elif num_max_scores == 1:
            solo_win += outcome.probability
        else:
            other_outcome += outcome.probability

    print(f"\tsolo win: {round(solo_win, 3)}")
    print(f"\ttwo win: {round(two_win, 3)}")
    print(f"\tthree win: {round(three_win, 3)}")
    print(f"\tfour win: {round(four_win, 3)}")
    print(f"\tother outcome: {round(other_outcome, 3)}")


def winning_score_probability(outcomes: list[Outcome]):
    print("Probabilities of winning score of finalists.")
    winning_scores = defaultdict(float)
    for outcome in outcomes:
        max_score = max(outcome.results.values())
        winning_scores[max_score] += outcome.probability

    print(winning_scores)


def per_player_finalist_probabilities(outcomes: list[Outcome]):
    print("Probabilities of each player being a finalist")
    for player in outcomes[0].results.keys():
        win_probability = 0.0
        for outcome in outcomes:
            if outcome.results[player] == max(outcome.results.values()):
                win_probability += outcome.probability

        if win_probability > 0.0:
            print(f"\t{player.name}: {round(win_probability, 3)}")



def expected_score(opponent_ratings: list[float], own_rating: float) -> float:
    """How many points we expect to score in games with these opponents"""
    return sum(
        1 / (1 + 10 ** ((opponent_rating - own_rating) / 400))
        for opponent_rating in opponent_ratings
    )


def performance_rating(opponent_ratings: list[float], score: float) -> int:
    """Calculate mathematically perfect performance rating with binary search."""
    lo, hi = 0, 5000

    while hi - lo > 0.0001:
        mid = (lo + hi) / 2

        if expected_score(opponent_ratings, mid) < score:
            lo = mid
        else:
            hi = mid

    return round(mid)


def get_players_performance_rating() -> tuple[dict[str, Player], Outcome]:
    player_performance: dict[str, dict[str, list | float]] = {}
    players: list[Player] = []
    with open("2024-fide-candidates-chess-tournament.pgn", "r") as in_file:
        game = read_headers(in_file)
        while game is not None:
            if Player(game["White"], int(game["WhiteElo"])) not in players:
                players.append(Player(game["White"], int(game["WhiteElo"])))
            if Player(game["Black"], int(game["BlackElo"])) not in players:
                players.append(Player(game["Black"], int(game["BlackElo"])))

            if game["Result"] == "*":
                game = read_headers(in_file)
                continue

            white_result = 0.5
            white_result = 1 if game["Result"] == "1-0" else white_result
            white_result = 0 if game["Result"] == "0-1" else white_result

            if game["White"] not in player_performance:
                player_performance[game["White"]] = {
                    "opponents": [],
                    "fide": int(game["WhiteElo"]),
                    "score": 0.0,
                }
            if game["Black"] not in player_performance:
                player_performance[game["Black"]] = {
                    "opponents": [],
                    "fide": int(game["BlackElo"]),
                    "score": 0.0,
                }

            player_performance[game["White"]]["opponents"].append(
                int(game["BlackElo"])
            )
            player_performance[game["White"]]["score"] += white_result
            player_performance[game["Black"]]["opponents"].append(
                int(game["WhiteElo"])
            )
            player_performance[game["Black"]]["score"] += 1 - white_result

            game = read_headers(in_file)

    for player in players:
        if player.name not in player_performance:
            player_performance[player.name] = {
                "opponents": [],
                "fide": player.rating,
                "score": 0.0,
            }

    performance_ratings: dict[str, Player] = {
        name: (
            Player(name, performance_rating(data["opponents"], data["score"]))
            if data["opponents"] and data["score"]
            else Player(name, data["fide"])
        )
        for name, data in player_performance.items()
    }

    results = {
        Player(name, performance_rating(data["opponents"], data["score"])): data[
            "score"
        ]
        for name, data in player_performance.items()
    }

    standings: Outcome = Outcome(
        {
            Player(name, performance_rating(data["opponents"], data["score"])): data[
                "score"
            ]
            for name, data in player_performance.items()
        },
        1.0,
    )

    return performance_ratings, standings


def get_pairings():
    output = []
    with open("2024-fide-candidates-chess-tournament.pgn", "r") as in_file:
        headers = read_headers(in_file)
        while headers is not None:
            if headers["Result"] != "*":
                headers = read_headers(in_file)
                continue

            output.append(
                (
                    headers["White"],
                    headers["Black"],
                )
            )

            headers = read_headers(in_file)

    return output


def group_outcomes(outcomes: list[Outcome]) -> list[Outcome]:
    # check the results of the outcomes and group them by the same results, adding the probabilities together
    results = {}
    for outcome in outcomes:
        if outcome not in results:
            results[outcome] = 0

        results[outcome] += outcome.probability

    return [
        Outcome(outcome.results, prob) for outcome, prob in results.items()
    ]


def main():
    performance_ratings, results = get_players_performance_rating()
    for name, player in performance_ratings.items():
        print(f"{name}: {player.rating}")
    future_pairs = get_pairings()
    pairings = [
        Pairing(performance_ratings[p1], performance_ratings[p2])
        for p1, p2 in future_pairs
    ]
    tournament = Tournament(
        standings=results, pairings=pairings
    )

    player_probabilities = tournament.run()
    solo_win_probabilities(player_probabilities)
    winning_score_probability(player_probabilities)
    per_player_finalist_probabilities(player_probabilities)


if __name__ == "__main__":
    main()
