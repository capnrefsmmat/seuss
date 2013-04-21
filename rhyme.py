#!/usr/bin/python

import Markov, sys, random, shelve, sqlite3

class RhymingMarkovGenerator:
    """Uses Markov to generate rhyming Markov chains."""
    
    """ Weights to use when calculating which words should be used next. These
    are largely arbitrary, and should be tinkered with."""
    frequencyWeight = 2
   
    def __init__(self, rhymescheme, personalities, lineLen = 10, cacheDir = ""):
        """ We require two different Markov chains of the same text to achieve
        poetry.  The forward chain is a simple forward-looking Markov chain that
        is used to generate lines when they have no need of rhyming -- for
        example, the first line of the poem.
        
        The reverse chain is a "backwards" chain: text is reversed before being
        processed by it. It is used to work backwards from the end of a line
        (and the rhyming word there) to the beginning.  The rhyme scheme is
        stored as a simple list, with each item in the list corresponding to one
        line in the poem."""
        
        self.rhymeScheme    = list(rhymescheme)
        self.lineLen        = lineLen

        if len(self.rhymeScheme) != len(list(personalities)):
            raise KeyError("personality list and rhyme scheme do not match")
        
        self.brains         = dict()
        self.personalities  = list(personalities)
        for personality in personalities:
            if not personality in self.brains:
                self.load(personality, cacheDir)

        self.rhymeDB             = sqlite3.connect("data/sql-words")
        self.rhymeDB.row_factory = sqlite3.Row
        self.rhymeDBc            = self.rhymeDB.cursor()
        
        self.poem           = [] # a poem is appended into poems
    
    def load(self, personality, cacheDir):
        """Load a personality into memory by loading its Markov chains"""
        
        self.brains[personality] = dict()
        self.brains[personality]["fwd"] = Markov.MarkovChain(cacheDir + personality + "-fwd", 
                                                             1, False)
        self.brains[personality]["rev"] = Markov.MarkovChain(cacheDir + personality + "-rev", 
                                                             1, False)
    
    def cleanWord(self, word):
        """ Get the junk off a word to look it up. """
        return word.strip().strip(".,'!?\"()*;:-")
    
    def getRhymeLine(self, lineNumber):
        """Return the line number of the line which this lineNumber must rhyme
        with."""
        return self.rhymeScheme.index(self.rhymeScheme[lineNumber], 0,
                                      lineNumber)

    def getRhymes(self, word):
        """Find the rhymes of word. Return them in random order."""
        word = self.cleanWord(word.lower())
        self.rhymeDBc.execute("SELECT rhymes.words FROM rhymes, words\
                               WHERE words.rhymes = rhymes.id\
                               AND words.word = ?", (word,))
        r = self.rhymeDBc.fetchone()

        if r == None:
            return None

        rhymes = r[0].split()
        random.shuffle(rhymes)
        return rhymes
    
    def getRhymingWord(self, curLine, person):
        """What word should go on the end of this line so it rhymes with the
        previous?"""
        
        try:
            rhymeLine = self.getRhymeLine(curLine)
        except ValueError:
            return None

        rhymeWord = self.poem[rhymeLine].split()[-1]
        
        rhymes = self.getRhymes(rhymeWord)
        if rhymes == None:
            return None
        
        # now we look for rhyming words in our chain
        for rhyme in rhymes:
            word = self.brains[person]["rev"].chain.get(str(rhyme.lower()))
            if (word is not None and
                rhyme.lower() != self.cleanWord(rhymeWord.lower())):
                return rhyme.lower()

        # the loop exited without breaking, so we found no rhymes that exist in
        # our Markov chains
        return None
        
    def addWords(self, numWords, brain, chain, line):
        """We query our Markov chain to get the next words possible in this
           line. We weight the words according to their frequency, then choose a
           word using those weights."""
       
        totalWeight = 0

        for i in range(numWords):
            words = self.brains[brain][chain].getNextWords(line)
            
            if len(words) == 0:
                return ([], 0) # do nothing, we give up
            
            weightedWords = dict()
            for word, num in words.iteritems():
                weightedWords[word] = num * self.frequencyWeight
            
            # do a weighted random selection from the words
            rand = random.randint(0, sum(weightedWords.values()))
            pos = 0
            for word, weight in weightedWords.items():
                pos += weight
                if rand <= pos:
                    line.append(word)
                    totalWeight += weight
                    break

        return (line, totalWeight)
    
    def getLine(self, person, curLine): 
        # right, what shall we rhyme with?
        newWord = self.getRhymingWord(curLine, person)
        weight = 0

        line = []

        if newWord is not None:
            line.append(newWord)
            words, weight = self.addWords(self.lineLen - 1, person,
                                          "rev", line)
            line.reverse()
        else:
            # found no rhyme, or perhaps this line doesn't need to rhyme.
            words, weight = self.addWords(self.lineLen, person,
                                          "fwd", line)
                        
        return line
    
    def getPoem(self):
        """Get a poem, according to our set rhymescheme and personality."""
        
        self.poem = []
        for i in range(len(self.rhymeScheme)):
            if self.rhymeScheme[i] == ":":
                # : serves as a stanza separator in multi-stanza rhyme schemes.
                # we insert a newline and go to the next stanza
                self.poem.append("\n")
                continue
            
            person = self.personalities[i] # what brain are we rhyming with?
            
            self.poem.append(" ".join(self.getLine(person, i)))
    
    def __iter__(self):
        return self
    
    def next(self):
        self.getPoem()
        return self.poem
    
    def close(self):
        """Make sure our brains are closed so they save their contents."""
        for name, brain in self.brains.items():
            brain['fwd'].close()
            brain['rev'].close()
        

people = {"b": "bible", "e": "erotica", "c": "carroll", "u": "unabomber",
          "w": "weeping", "j": "ulysses", "l": "legal", "k": "kafka",
          "t": "twain", "s": "kamasutra", "x": "wikisex", "g": "starwars",
          "f": "fanny-hill", "a": "fiftyshades", "d": "dprk",
          "n": "bergson"}

if __name__ == "__main__":         
    if len(sys.argv) < 5:
        print """Usage:
rhyme.py personality rhymescheme linelength numpoems
    
where personality is a choice of personality, rhymescheme is a rhyme scheme,
such as "aaaba", linelength is an integer representing the maximum number of
words per line, and numpoems is the number of repetitions desired.

Personality choices are per-line, so personality must match rhymescheme in 
length. Each character corresponds to a personality.

If a rhyme scheme spans multiple stanzas, it can be specified as follows:
  abab:cdcd:ee
and so on. The ":" characters indicate a stanza division.

If numlines is larger than the size the rhyme scheme indicates, multiple
repetitions of the rhyme scheme will be made. Only whole repetitions are
attemped, so if the rhyme scheme is five lines long and numlines 7, only one
set will be constructed. Once numlines is raised to 10, the rhyme scheme will
be repeated once in another set of stanzas."""
        print ""
        print "Available personalities:"
        for char, personality in people.items():
            print char, personality
        sys.exit(1)
    
    personality = sys.argv[1]
    rhymescheme = sys.argv[2]
    lineLength  = int(sys.argv[3])
    numPoems    = int(sys.argv[4])
    
    cacheDir = "cache/"
    
    personalities = []
    for personality in list(personality):
        personalities.append(people[personality])
    
    gen = RhymingMarkovGenerator(rhymescheme, personalities, lineLength, cacheDir)
    
    for i in range(numPoems):
        poem = gen.next()
        for line in poem:
            print line
        print ""
    
    gen.close()
