"""
Get the difference between player "official" ratings and online ratings.
"""
import csv
from typing import NamedTuple

from tqdm import tqdm
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


country_codes = [
    "AF",
    "AX",
    "AL",
    "DZ",
    "AS",
    "AD",
    "AO",
    "AI",
    "AQ",
    "AG",
    "AR",
    "AM",
    "AW",
    "AU",
    "AT",
    "AZ",
    "BS",
    "BH",
    "BD",
    "BB",
    "BY",
    "BE",
    "BZ",
    "BJ",
    "BM",
    "BT",
    "BO",
    "BA",
    "BW",
    "BV",
    "BR",
    "VG",
    "IO",
    "BN",
    "BG",
    "BF",
    "BI",
    "KH",
    "CM",
    "CA",
    "CV",
    "KY",
    "CF",
    "TD",
    "CL",
    "CN",
    "HK",
    "MO",
    "CX",
    "CC",
    "CO",
    "KM",
    "CG",
    "CD",
    "CK",
    "CR",
    "CI",
    "HR",
    "CU",
    "CY",
    "CZ",
    "DK",
    "DJ",
    "DM",
    "DO",
    "EC",
    "EG",
    "SV",
    "GQ",
    "ER",
    "EE",
    "ET",
    "FK",
    "FO",
    "FJ",
    "FI",
    "FR",
    "GF",
    "PF",
    "TF",
    "GA",
    "GM",
    "GE",
    "DE",
    "GH",
    "GI",
    "GR",
    "GL",
    "GD",
    "GP",
    "GU",
    "GT",
    "GG",
    "GN",
    "GW",
    "GY",
    "HT",
    "HM",
    "VA",
    "HN",
    "HU",
    "IS",
    "IN",
    "ID",
    "IR",
    "IQ",
    "IE",
    "IM",
    "IL",
    "IT",
    "JM",
    "JP",
    "JE",
    "JO",
    "KZ",
    "KE",
    "KI",
    "KP",
    "KR",
    "KW",
    "KG",
    "LA",
    "LV",
    "LB",
    "LS",
    "LR",
    "LY",
    "LI",
    "LT",
    "LU",
    "MK",
    "MG",
    "MW",
    "MY",
    "MV",
    "ML",
    "MT",
    "MH",
    "MQ",
    "MR",
    "MU",
    "YT",
    "MX",
    "FM",
    "MD",
    "MC",
    "MN",
    "ME",
    "MS",
    "MA",
    "MZ",
    "MM",
    "NA",
    "NR",
    "NP",
    "NL",
    "AN",
    "NC",
    "NZ",
    "NI",
    "NE",
    "NG",
    "NU",
    "NF",
    "MP",
    "NO",
    "OM",
    "PK",
    "PW",
    "PS",
    "PA",
    "PG",
    "PY",
    "PE",
    "PH",
    "PN",
    "PL",
    "PT",
    "PR",
    "QA",
    "RE",
    "RO",
    "RU",
    "RW",
    "BL",
    "SH",
    "KN",
    "LC",
    "MF",
    "PM",
    "VC",
    "WS",
    "SM",
    "ST",
    "SA",
    "SN",
    "RS",
    "SC",
    "SL",
    "SG",
    "SK",
    "SI",
    "SB",
    "SO",
    "ZA",
    "GS",
    "SS",
    "ES",
    "LK",
    "SD",
    "SR",
    "SJ",
    "SZ",
    "SE",
    "CH",
    "SY",
    "TW",
    "TJ",
    "TZ",
    "TH",
    "TL",
    "TG",
    "TK",
    "TO",
    "TT",
    "TN",
    "TR",
    "TM",
    "TC",
    "TV",
    "UG",
    "UA",
    "AE",
    "GB",
    "US",
    "UM",
    "UY",
    "UZ",
    "VU",
    "VE",
    "VN",
    "VI",
    "WF",
    "EH",
    "YE",
    "ZM",
    "ZW",
]


class UserStats(NamedTuple):
    username: str
    fide: int | None
    bullet: int | None
    blitz: int | None
    rapid: int | None

    def to_dict(self):
        return {
            "username": self.username,
            "fide": self.fide,
            "bullet": self.bullet,
            "blitz": self.blitz,
            "rapid": self.rapid,
        }


def get_titled_players() -> list:
    players = []
    for title in ["GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM"]:
        response = requests.get(f"https://api.chess.com/pub/titled/{title}").json()
        players.extend(response["players"])

    return players


def get_rating_stats(username):
    response = requests.get(f"https://api.chess.com/pub/player/{username}/stats").json()

    fide_rating = response.get("fide")
    bullet_rating = response.get("chess_bullet", {}).get("last", {}).get("rating")
    blitz_rating = response.get("chess_blitz", {}).get("last", {}).get("rating")
    rapid_rating = response.get("chess_rapid", {}).get("last", {}).get("rating")

    return UserStats(
        username,
        fide_rating,
        bullet_rating,
        blitz_rating,
        rapid_rating,
    )


def main():
    usernames = get_titled_players()

    try:
        processed_df = pd.read_csv("processed_users.csv")
        processed_usernames = set(processed_df["username"].to_list())

    except FileNotFoundError:
        processed_usernames = set()

    with open('processed_users.csv', 'a', newline='') as csvfile:
        fieldnames = ['username', 'fide', 'bullet', 'blitz', 'rapid']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not processed_usernames:
            writer.writeheader()

        for username in tqdm(usernames):
            if username in processed_usernames:
                continue

            user = get_rating_stats(username)
            writer.writerow(user.to_dict())

            processed_usernames.add(username)

    processed_df = pd.read_csv("processed_users.csv")
    processed_df = processed_df.loc[processed_df["fide"].notna()]
    processed_df = processed_df.loc[processed_df["fide"] > 0]
    x = []
    y = []

    for row, user in tqdm(processed_df.iterrows(), total=len(processed_df)):
        if user["rapid"] > 0 and user["rapid"] != np.nan:
            x.append(user["rapid"])
            y.append(user["fide"])

    plt.scatter(x, y, alpha=0.5)
    plt.xlabel('chess.com rapid rating')
    plt.ylabel('self-reported rating')

    rapid_diff = [user['rapid'] - user['fide'] for _, user in processed_df.iterrows()]

    print("Rapid")
    print(f"\tMean: {np.mean(rapid_diff)}")
    print(f"\tMedian: {np.median(rapid_diff)}")
    print(f"\tStd: {np.std(rapid_diff)}")

    print(f"Biggest Rapid Difference: {max(rapid_diff)}")

    plt.show()


if __name__ == "__main__":
    main()
