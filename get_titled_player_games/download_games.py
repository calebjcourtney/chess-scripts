"""
Get the games between all titled players. Note that this will take a *very* long time to download all the data.
It would be nice if Chess.com made it simpler to generate downloadable archives, given certain queryies.

This is essentially a
SELECT pgn
FROM database
WHERE white IN titled_players AND black IN titled_players
"""
from typing import List


from urllib.parse import urlparse
import os
from datetime import datetime
import time
import json
import sqlite3

import requests
from tqdm import tqdm


cur_year = datetime.now().year
cur_month = datetime.now().month


connection = sqlite3.connect("processed_archives.db")
cursor = connection.cursor()
sql = "CREATE TABLE IF NOT EXISTS archives (archive TEXT)"
cursor.execute(sql)


def get_processed_archives(username) -> List[str]:
    sql = """
        SELECT archive
        FROM archives
        WHERE archive LIKE '%_{}_%'
    """.format(username)

    cursor.execute(sql)
    return [row[0] for row in cursor.fetchall()]


def add_processed_archives(url_name: str) -> None:
    sql = """
        INSERT INTO archives (archive)
        VALUES ('{}')
    """.format(url_name)

    cursor.execute(sql)
    connection.commit()


def get_titled_players() -> List[str]:
    players = []
    for title in ["GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM"]:
        response = requests.get(f"https://api.chess.com/pub/titled/{title}").json()
        players.extend(response["players"])

    return players


def main():
    processed_archives = os.listdir("raw_data")
    players = get_titled_players()
    for player in tqdm(players):
        player_processed_archives = get_processed_archives(player)
        archives_response = requests.get(f"https://api.chess.com/pub/player/{player}/games/archives").json()
        archive_urls = [
            url for url in archives_response["archives"]
            if f"{cur_year}/{cur_month}" not in url
            and url not in player_processed_archives
        ]
        for archive_url in archive_urls:
            info = urlparse(archive_url)

            if f"{info.path.replace('/', '_')}.json" in processed_archives:
                continue

            data = requests.get(archive_url, headers={"Accept-Encoding": "gzip"}).json()
            data = [
                record
                for record in data["games"]
                if record["rules"] == "chess"
                and record["white"]["username"] in players
                and record["black"]["username"] in players
            ]
            if data:
                with open(f"raw_data/{info.path.replace('/', '_')}.json", "w+") as out_file:
                    json.dump(data, out_file)

                time.sleep(0.1)

            add_processed_archives(archive_url)

        time.sleep(0.1)


if __name__ == '__main__':
    main()
