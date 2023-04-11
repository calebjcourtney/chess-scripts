import os
import json

from tqdm import tqdm
import requests


def get_titled_players() -> set:
    players = []
    for title in ["GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM"]:
        response = requests.get(f"https://api.chess.com/pub/titled/{title}").json()
        players.extend(response["players"])

    return set(players)


titled_players = get_titled_players()

processed_games = set()

out_file = open(f"titled_games/titled_games.pgn", "w+")

game_count = 0

for file_name in tqdm(os.listdir("raw_data")):
    if not file_name.endswith(".json"):
        continue

    data = json.load(open(f"raw_data/{file_name}", "r"))
    for game in data:
        if (
            game["rules"] != "chess"
            or game["white"]["username"] not in titled_players
            or game["black"]["username"] not in titled_players
        ):
            continue

        pgn = game["pgn"]
        out_file.write(pgn)
        out_file.write("\n")

        game_count += 1

print(game_count)
