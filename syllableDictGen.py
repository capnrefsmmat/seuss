#!/usr/bin/python
"""Using cmudict, make a Shelve database of word->syllables pairs. Update
   cmudict.txt to the latest version of the cmudict to get best results."""

import sqlite3

conn = sqlite3.connect("data/sql-words")
conn.row_factory = sqlite3.Row

c = conn.cursor()


f = open("data/cmudict.txt", "r")

for line in f:
    if line.startswith(";;;"):
        continue
    
    item = line.split(None, 1) # split word and pronunciation apart
    word = item[0].lower()
    syllables = item[1]

    c.execute("UPDATE words SET syllables = ? WHERE word = ?", (syllables, word))

conn.commit()
