"""
Get the top players (by username) for a given game format.
"""
from urllib.parse import urlparse
import os
from datetime import datetime

import requests
from tqdm import tqdm


cur_year = datetime.now().year
cur_month = datetime.now().month


def get_titled_players() -> list:
    players = []
    for title in ["GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM"]:
        response = requests.get(f"https://api.chess.com/pub/titled/{title}").json()
        players.extend(response["players"])

    return players


def main():
    processed_archives = os.listdir("raw_data")
    players = get_titled_players()
    for player in tqdm(players):
        archives_response = requests.get(f"https://api.chess.com/pub/player/{player}/games/archives").json()
        archive_urls = [
            url for url in archives_response["archives"]
            if f"{cur_year}/{cur_month}" not in url
        ]
        for archive_url in archive_urls:
            info = urlparse(archive_url)

            if f"{info.path.replace('/', '_')}.json" in processed_archives:
                continue

            data = requests.get(archive_url, headers={"Accept-Encoding": "gzip"})
            with open(f"raw_data/{info.path.replace('/', '_')}.json", "wb") as out_file:
                out_file.write(data.content)


if __name__ == '__main__':
    main()
