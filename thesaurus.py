import shelve

class Thesaurus:
    def __init__(self, wordsDB, synsDB):
        self.words = shelve.open(wordsDB, protocol = 2)
        self.syns = shelve.open(synsDB, protocol = 2)
        self.synCache = dict()
    
    def getSynonyms(self, word):
        """Also based on wordnet.py with some modifications -- see
           createThesaurus.py for details"""
        syns = set()
        
        try:
            keys = self.words[word]
        except KeyError:
            return syns
        
        for key in keys:
            syns = syns.union(self.syns[str(key)])
        
        if word in syns:
            syns.remove(word)
        
        return syns
    
    def getListSynonyms(self, line):
        """Get a list of synonyms of every word in a list of words."""
        if tuple(line) in self.synCache:
            return list(self.synCache[tuple(line)])
        
        syns = set()
        for word in line:
            syns = syns.union(self.getSynonyms(word))
        
        self.synCache[tuple(line)] = syns
        return list(syns)

if __name__ == "__main__":
    # test that the thesaurus is functional
    thes = Thesaurus("data/thesaurusWords", "data/thesaurusSyns")
    
    print thes.getSynonyms("car")