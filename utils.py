import csv


class MyCsvDialect(csv.Dialect):
    delimiter = ","
    escapechar = '\\'
    doublequote = False
    skipinitialspace = True
    lineterminator = '\n'
    quoting = csv.QUOTE_ALL
    quotechar = '"'
