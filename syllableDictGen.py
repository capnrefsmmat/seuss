#!/usr/bin/python
"""Using cmudict, make a Shelve database of word->syllables pairs. Update
   cmudict.txt to the latest version of the cmudict to get best results."""

import shelve

f = open("cmudict.txt", "r")
db = shelve.open("syllableDB", protocol = 2)

for line in f:
    if line.startswith(";;;"):
        continue
    
    item = line.split(None, 1) # split word and pronunciation apart
    key = item[0].replace("_", " ") # two-word keys use _ as a separator
    value = filter(str.isdigit, item[1]) # only return syllable weighting
    
    db[key] = value

db.close()
