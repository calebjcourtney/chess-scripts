import requests
from tqdm import tqdm
import time


HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.6",
    "cache-control": "max-age=0",
    "if-modified-since": "Thursday, 20-Feb-2025 17:48:57 GMT+0000",
    "if-none-match": '''"W/"d5219b33d67106db51abd52bb0ef9f60"''',
    "priority": "u=0, i",
    "sec-ch-ua": '''"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"''',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '''"macOS"''',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Cookie": "me=%7B%22deviceId%22%3A%220a56e2ae-ef2d-11ef-8248-5b9f74f65146%22%7D; psid=a3dae162-efb1-11ef-94a9-6b33d94997b1; PHPSESSID=f5fb661907a36638f27c9ea1e94a9710; __cf_bm=IG78cJnEumYofd.fSYB3CZHrFlWK3ku9L0RDd37Z5L4-1740073171-1.0.1.1-3oEJxQJ_JXdx.yaqeOvoby3GNRPy_lK.7ZlR15jOSqABAXBiksjDEPsxLe_C2hvsr3P2KQY18Xzt1plbxrf76Z9chAs6p8Brein5PnJv1Sg; ATTRIBUTION_V1=%7B%22initialAttribution%22%3A%7B%22source%22%3A%22unknown%22%2C%22medium%22%3A%22unknown%22%2C%22campaign%22%3Anull%2C%22term%22%3Anull%2C%22content%22%3Anull%2C%22route%22%3A%22%5C%2F%22%2C%22referer%22%3A%22unknown%22%2C%22version%22%3A%221.0.0%22%2C%22createDateTime%22%3A%221740016219%22%7D%2C%22lastAttribution%22%3A%7B%22source%22%3A%22unknown%22%2C%22medium%22%3A%22unknown%22%2C%22campaign%22%3Anull%2C%22term%22%3Anull%2C%22content%22%3Anull%2C%22route%22%3A%22%5C%2Fmember%5C%2FAnilyamdav%22%2C%22referer%22%3A%22unknown%22%2C%22version%22%3A%221.0.0%22%2C%22createDateTime%22%3A%221740073490%22%7D%7D; amp_5cc41a=0a56e2ae-ef2d-11ef-8248-5b9f74f65146.NDk1MDE1NjY=..1iki72v9c.1iki7cmqk.0.5.5"
}


PLAYERS = [
    "caleb-courtney",
]


# def get_titled_players() -> list:
#     players = []
#     for title in ["GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM"]:
#         response = requests.get(
#             f"https://api.chess.com/pub/titled/{title}", headers=HEADERS
#         ).json()
#         players.extend(response["players"])

#     return {p.lower() for p in players}


# TITLED_PLAYERS = get_titled_players()


def get_opponents(player, time_control="180") -> set[str]:
    output = set()
    archives_url = f"https://api.chess.com/pub/player/{player}/games/archives"
    archives_response = requests.get(archives_url, headers=HEADERS)
    urls = archives_response.json()["archives"]
    print(urls)
    urls.sort(reverse=True)
    num_games = 0
    for url in tqdm(urls):
        if len(output) >= 100:
            continue

        time.sleep(0.5)

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
            output.add(game["white"]["username"])
            output.add(game["black"]["username"])
            # if game["time_control"] != time_control:
            #     continue

            # if (
            #     game["white"]["rating"] > 2500
            #     and game["white"]["username"].lower() not in TITLED_PLAYERS
            # ):
            #     num_games += 1
            #     output.add(game["white"]["username"])
            # if (
            #     game["black"]["rating"] > 2500
            #     and game["black"]["username"].lower() not in TITLED_PLAYERS
            # ):
            #     num_games += 1
            #     output.add(game["black"]["username"])

            if len(output) >= 1000:
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
        profile_data = profile.json()
        if "status" not in profile_data:
            print(profile_data)
        if "closed" in profile_data.get("status", ""):
            print(profile.text)
            cheaters.append(opp)
            print(cheaters)

    print(cheaters)
    print(len(cheaters))


if __name__ == "__main__":
    main()
