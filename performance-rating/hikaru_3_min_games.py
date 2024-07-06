import requests

# links to all the archives of games Hikaru has played
url = f"https://api.chess.com/pub/player/hikaru/games/archives"
archives = requests.get(url)
archives = archives.json()["archives"]
archives.sort()

games_played = 0
for url in archives:
    # get the games played that month
    archive_response = requests.get(url).json()

    # iterate through each game
    for game_json in archive_response["games"]:
        # must be a game of chess, not a variant
        if game_json["rules"] != "chess":
            continue

        # must be a rated game
        if not game_json["rated"]:
            continue

        # must be a blitz game
        if game_json["time_control"] != "180":
            continue

        games_played += 1

print(games_played)
