"""
Carga los listados de top en un único archivo
"""
import csv
import os
import re
import warnings
from typing import Tuple, Any, List

import spotipy as spotipy
from librespot.core import Session

from utils import MyCsvDialect

SPOTIFY_USER = os.environ.get("SPOTIFY_USER")
SPOTIFY_PASSWORD = os.environ.get("SPOTIFY_PASSWORD")
QUERY_LIMIT = 100  # Less than 400
SPECIAL_ARTIST_NAMES = ["t-rex", "m-clan"]


def clean_field(s: str) -> str:
    return s.strip().lower()


def get_track_info(playlist_item: dict) -> Tuple[Any, ...]:
    targets = (playlist_item["track"]["artists"][0]["name"],
               playlist_item["track"]["name"],
               playlist_item["track"]["artists"][0]["id"],
               playlist_item["track"]["id"])
    return tuple(map(lambda x: clean_field(x), targets))


def split_info(s: str) -> List[str]:
    cleaned_str = clean_field(s)
    for artist in SPECIAL_ARTIST_NAMES:
        if cleaned_str.startswith(artist):  # It's a special case
            warnings.warn(f'Special artist name found "{artist}" fixing')
            cleaned_str = cleaned_str.replace(artist, artist.replace("-", "_"))
            special_name = True
            break
    else:
        special_name = False

    parts = cleaned_str.strip().split("-", maxsplit=1)
    if len(parts) != 2:
        parts = s.split("\u2013", maxsplit=1)

    # Set original name again
    if special_name:
        parts[0] = parts[0].replace("_", "-")

    if len(parts) != 2:
        warnings.warn(f'Please check payload "{s}"')

    return parts


playlists_ids = ["4HJLf64sNkUdFNMZVqXyhI", "6JSrzTWHiKDea83DFf0KcW", "7jB1GygtJchkY9AHmO8ZGX"]  # 2016-2018

headers = ["artist", "song", "artists_id", "song_id"]

with open(f"data/top_500.csv", "w", encoding="utf*") as csv_file:
    writer = csv.writer(csv_file, MyCsvDialect)
    writer.writerow(headers)

    for i in range(3, 6, 1):
        with open(f"data/raw/top500_201{i}.txt", "r", encoding="utf8") as f:  # 2013-2015
            f.readline()  # Skip source line
            for line in f:
                if line != "":  # Ignore blank lines
                    payload = line.strip().split("→")[1]
                    writer.writerow([clean_field(x) for x in split_info(payload)] + [""] * 2)

    session = Session.Builder().user_pass(SPOTIFY_USER, SPOTIFY_PASSWORD).create()
    token = session.tokens().get_token('playlist-read').access_token
    spotify = spotipy.Spotify(auth=token)

    for playlist_id in playlists_ids:  # 2016-2018
        offset = 0
        total_tracks = offset + 1  # First try it's free!
        while offset < total_tracks:
            tracks = spotify.playlist_items(playlist_id, additional_types=("track",), limit=QUERY_LIMIT,
                                            offset=offset)
            offset += QUERY_LIMIT
            total_tracks = tracks["total"]
            for item in tracks["items"]:
                writer.writerow(get_track_info(item))

    for i in range(19, 22, 1):  # 2019-2021
        with open(f"data/raw/top500_20{i}.txt", "r", encoding="utf8") as f:  # 2019-2021
            f.readline()  # Skip source line
            expression = re.compile(r"^(\s*\d+\s*\.).*")
            for n, line in enumerate(f):
                m = expression.match(line)
                if m:
                    payload = line.replace(m.group(1), "").strip()
                    writer.writerow([clean_field(x) for x in split_info(payload)] + [""] * 2)
