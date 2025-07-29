"""
Module
"""
def year(data):
    year = input("What year? ")
    for row in data:
        cells = row.split(",")

        if cells[3] == year:
            print(cells[2], end=":")
            get_with_key(cells[0], -1)

def get_with_key(key, column):
    with open("title.ratings.csv") as fd:
        rows = fd.read().split("\n")
        for row in rows:
            cells = row.split(",")
            if cells[0] == key:
                print(cells[column])