import requests
from tqdm import tqdm
import time


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


PLAYERS = [
    "msb2",
    "hikaru",
    "jospem",
    "oleksandr_bortnyk",
]


def get_titled_players() -> list:
    players = []
    for title in ["GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM"]:
        response = requests.get(
            f"https://api.chess.com/pub/titled/{title}", headers=HEADERS
        ).json()
        players.extend(response["players"])

    return {p.lower() for p in players}


TITLED_PLAYERS = get_titled_players()


def get_opponents(player, time_control="180") -> set[str]:
    output = set()
    archives_url = f"https://api.chess.com/pub/player/{player}/games/archives"
    archives_response = requests.get(archives_url, headers=HEADERS)
    urls = archives_response.json()["archives"]
    urls.sort(reverse=True)
    num_games = 0
    for url in tqdm(urls):
        if num_games > 3000:
            continue

        time.sleep(1.5)

        response = requests.get(url, headers=HEADERS)
        if response.json() == {
            "code": 0,
            "message": "An internal error has occurred. Please contact Chess.com Developer's Forum for further help https://www.chess.com/club/chess-com-developer-community .",
        }:
            continue

        try:
            games = response.json()["games"]
        except KeyError:
            print(response.text)
            time.sleep(10)
            response = requests.get(url, headers=HEADERS)
            games = response.json()["games"]

        for game in games:
            if game["time_control"] != time_control:
                continue

            if (
                game["white"]["rating"] > 2500
                and game["white"]["username"].lower() not in TITLED_PLAYERS
            ):
                num_games += 1
                output.add(game["white"]["username"])
            if (
                game["black"]["rating"] > 2500
                and game["black"]["username"].lower() not in TITLED_PLAYERS
            ):
                num_games += 1
                output.add(game["black"]["username"])

            if num_games >= 3000:
                break

    return output


def main():
    opponents = set()
    for player in PLAYERS:
        print(player)
        opponents |= get_opponents(player)

    cheaters = []

    print("trying to get cheaters")
    for opp in tqdm(opponents):
        url = f"https://api.chess.com/pub/player/{opp}"
        profile = requests.get(url, headers=HEADERS)
        print(profile.text)
        if profile.status_code != 200:
            cheaters.append(opp)
            print(cheaters)

    print(cheaters)
    print(len(cheaters))


if __name__ == "__main__":
    main()
