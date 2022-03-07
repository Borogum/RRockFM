"""
Transforma los ficheros top de los años 13,14 y 15 en un csv
"""
import csv

from utils import MyCsvDialect

headers = ["artist", "title", "spotify_id"]

for i in range(3, 6, 1):
    with open(f"data/raw/top500_201{i}.txt", "r", encoding="utf8") as f, open(f"data/top_201{i}.csv",
                                                                              "w", encoding="utf*") as g:
        f.readline()  # Skip source line
        writer = csv.writer(g, MyCsvDialect)
        writer.writerow(headers)
        for line in f:
            if line != "":  # Ignore blank lines
                payload = line.strip().split("→")[1]
                writer.writerow([x.strip().lower() for x in payload.split("-", maxsplit=1)] + [None])
