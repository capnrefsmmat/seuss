#!/usr/bin/python
"""
 Portions of this file are based on wordnet.py, part of the Whoosh project
 and copyright 2009 Matt Chaput. Whoosh is available under the Apache License
 2.0.
 
 This file generates a thesaurus from Princeton's WordNet database.
"""

import shelve
from collections import defaultdict

# from wordnet.py
def parse_file(f):
    """Parses the WordNet wn_s.pl prolog file and returns two dictionaries:
    word2nums and num2words.
    """
    
    word2nums = defaultdict(list)
    num2words = defaultdict(list)
    
    for line in f:
        if not line.startswith("s("):
            continue
        
        line = line[2:]
        num = int(line[:line.find(",")])
        qt = line.find("'")
        line = line[qt + 1:]
        qt = line.find("'")
        word = line[:qt].lower()
        
        if not word.isalpha():
            continue
        
        word2nums[word].append(num)
        num2words[num].append(word)
    
    return word2nums, num2words

def stickInShelve(db, data):
    """Stick an arbitrary dict of data into Shelve."""
    
    for word in data.iteritems():
        db[str(word[0])] = word[1]

words = shelve.open("data/thesaurusWords", protocol = 2)
syns = shelve.open("data/thesaurusSyns", protocol = 2)

(word2nums, num2words) = parse_file(open('./data/wn_s.pl'))

stickInShelve(words, word2nums)
stickInShelve(syns, num2words)

words.close()
syns.close()