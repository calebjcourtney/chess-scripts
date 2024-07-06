import argparse
import json
from thefuzz import fuzz


def main(player_name):
    with open("titled_players.json") as in_file:
        data = json.load(in_file)

    for username, user_data in data.items():
        if "name" in user_data and fuzz.ratio(user_data["name"], player_name) >= 90:
            print(json.dumps(user_data))


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('player_name', type=str)
    args = argument_parser.parse_args()
    main(args.player_name)
