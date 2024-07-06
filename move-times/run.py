import requests
from io import StringIO
import re
import matplotlib.pyplot as plt
import statistics

import chess.pgn as pgn

CLOCK_PATTERN = re.compile(
    r"(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+(?:\.\d+)?)"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


PLAYERS_TO_COMPARE = [
    "MagnusCarlsen",
    "Hikaru",
    "Polish_fighter3000",
    "FairChess_on_YouTube",
    "Msb2",
    "Oleksandr_Bortnyk",
    "VladimirKramnik",
]
PLAYERS_TO_COMPARE = [
    "AnishOnYoutube",
    "LevonAronian",
    "VladimirKramnik",
]
SENIORS = [
    "tigrvshlyape",
    "alexrustemov",
    "mikhail_golubev",
    "bazar-wokzal",
    # igor yagupov
    "alexeishirov",
    "zq1",
    # Daniel Barria Zuniga
    "ural58",
    "emeli_chess",
]

JUNIORS = [
    "bardartem",
    "denlaz",
    "vi_pranav",
    "dearron_fox",
    "atm622",
    "only_strong_moves",
    "rantomopening",
    "nindjaxx8",
    "adar_07",
    "christopheryoo",
]


def get_move_stats(username):
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    archives = requests.get(url, headers=HEADERS)
    archives = [x for x in archives.json()["archives"] if "2024" in x]
    player_move_times = []

    for game_url in archives:
        print(game_url)
        month_data = requests.get(game_url, headers=HEADERS).json()
        for game in month_data["games"]:
            if "tournament" not in game or "titled-tuesday" not in game["tournament"]:
                continue

            if game["time_class"] != "blitz":
                continue

            side = 0 if game["white"]["username"].lower() == username.lower() else 1
            if "+" not in game["time_control"]:
                increment = 0
                time_control = int(game["time_control"])
            else:
                time_control, increment = map(int, game["time_control"].split("+"))

            # discount white's first move of the game, since it's a paired tournament and white (nearly) always pre-moves
            current_clock = time_control * 2
            first_move = True

            pgn_game = pgn.read_game(StringIO(game["pgn"]))

            for index, node in enumerate(pgn_game.mainline()):
                clock_time = str(node.comment)
                hours, minutes, seconds = CLOCK_PATTERN.search(clock_time).groups()

                seconds_left = float(seconds) + 60 * int(minutes) + 3600 * int(hours)
                if index % 2 == side:
                    if (
                        not first_move
                        and round(current_clock - (seconds_left - increment), 1)
                        < time_control
                    ):
                        # calculate the time spent by the player – make sure to add second for increment
                        player_move_times.append(
                            round(current_clock - (seconds_left - increment), 1)
                        )

                    current_clock = seconds_left
                    first_move = False

    return player_move_times


def get_group_data(group: list[str]) -> list[float]:
    move_times = []
    for username in group:
        move_times.extend(get_move_stats(username))

    return move_times


def graph_groups(group_data: dict[str, list[float]]):
    fig, axs = plt.subplots(len(group_data), 1, constrained_layout=True)

    for index, (name, times) in enumerate(group_data.items()):
        axs[index].hist(
            times,
            bins=100,
            color="c",
            edgecolor="k",
            alpha=0.65,
        )
        axs[index].axvline(
            statistics.mean(times),
            color="b",
            linestyle="dashed",
            linewidth=1,
        )
        axs[index].axvline(
            statistics.median(times),
            color="r",
            linestyle="dashed",
            linewidth=1,
        )
        axs[index].relim()
        max_ylim = max(axs[index].get_ylim())
        axs[index].text(
            statistics.mean(times) * 1.1,
            max_ylim * 0.6,
            "Mean: {:.2f}".format(statistics.mean(times)),
        )
        axs[index].text(
            statistics.median(times) * 1.1,
            max_ylim * 0.8,
            "Median: {:.2f}".format(statistics.median(times)),
        )
        axs[index].set_title(name)

    plt.savefig("/Users/caleb-courtney/Desktop/AnishLevonVlad.png")
    plt.show()


def juniors_vs_seniors():
    juniors_move_times = get_group_data(JUNIORS)
    juniors_move_times = [x for x in juniors_move_times if x < 100]
    seniors_move_times = get_group_data(SENIORS)
    seniors_move_times = [x for x in seniors_move_times if x < 100]

    graph_groups({"Juniors": juniors_move_times, "Seniors": seniors_move_times})


def main():
    graph_times = {}
    for username in PLAYERS_TO_COMPARE:
        move_times = get_move_stats(username)
        move_times = [x for x in move_times if x < 10]
        graph_times[username] = move_times

    graph_groups(graph_times)


if __name__ == "__main__":
    main()
