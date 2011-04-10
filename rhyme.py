#!/usr/bin/python

import Markov, sys, gdbm, random, shelve
from thesaurus import Thesaurus

class RhymingMarkovGenerator:
    """Uses Markov to generate rhyming Markov chains."""
    
    """ Weights to use when calculating which words should be used next. These are largely arbitrary,
    and should be tinkered with. """
    frequencyWeight = 2
    synonymWeight = 20

    # number of lines to try before picking the best line
    tryLines = 5
   
    def __init__(self, rhymescheme, personalities, lineLen = 10, sourceDir = "", cacheDir = ""):
        """ We require four different Markov chains of the same text to achieve poetry.
        The forward chain is a simple forward-looking Markov chain that is used to generate lines
        when they have no need of rhyming -- for example, the first line of the poem.
        The reverse chain is a "backwards" chain: text is reversed in word order before being processed
        by it. It is used to work backwards from the end of a line (and the rhyming word there) to the
        beginning.
        The rhyme chain is a first-order chain used to find the word before the word on the end of the
        line: the one before the rhyming word. 
        The rhyme scheme is stored as a simple list, with each item in the list corresponding to one
        line in the poem."""
        
        self.rhymeScheme    = list(rhymescheme)
        self.lineLen        = lineLen
        self.cacheDir       = cacheDir
        self.sourceDir      = sourceDir
        if len(self.rhymeScheme) != len(list(personalities)):
            raise KeyError("personality list and rhyme scheme do not match")
        
        self.brains         = dict()
        self.personalities  = list(personalities)
        for personality in personalities:
            if not personality in self.brains:
                self.load(personality)
        
        self.words          = gdbm.open("./data/words.db")
        self.rhymes         = gdbm.open("./data/rhymes.db")
        self.syllables      = shelve.open("data/syllableDB")
        self.thesaurus      = Thesaurus("data/thesaurusWords", "data/thesaurusSyns")
        
        self.poem           = [] # a poem is appended into poems
    
    def load(self, personality):
        """Load a personality into memory by loading its Markov chains"""
        
        self.brains[personality] = dict()
        self.brains[personality]["fwd"] = Markov.MarkovChain(self.cacheDir + personality + "-fwd", 
                                                             2, False)
        self.brains[personality]["rhy"] = Markov.MarkovChain(self.cacheDir + personality + "-rhy", 
                                                             1, False)
        self.brains[personality]["rev"] = Markov.MarkovChain(self.cacheDir + personality + "-rev", 
                                                             2, False)
    
    def cleanWord(self, word):
        """ Get the junk off a word to look it up. """
        return word.strip().strip(".,'!?\"()*;:-")
    
    def getRhymeLine(self, rhymeLetter, lineNumber):
        """Simple enough. Given our position in the poem, what line do we have to rhyme with?"""
        return self.rhymeScheme.index(rhymeLetter, 0, lineNumber)
            
    def getRhymingWord(self, curLine, person):
        """What word should go on the end of this line so it rhymes with the previous?"""
        
        try:
            rhymeLine = self.getRhymeLine(self.rhymeScheme[curLine], curLine) # get our line
        except ValueError:
            return False # no rhyming required, or the line has no words
        
        rhymeWord = self.poem[rhymeLine][-1]
        
        # get the list of rhymes of this word. shuffle it so we don't always choose
        # the same rhymes of the same word if we don't have to.
        try:
            rhymes = self.rhymes[self.words[self.cleanWord(rhymeWord.upper())].split()[0]].split()
        except KeyError:
            return False
        random.shuffle(rhymes)
        
        # now we look for rhyming words in our chain
        for rhyme in rhymes:
            word = self.brains[person]["rhy"].chain.get(rhyme.lower())
            if word is not None and rhyme.lower() != self.cleanWord(rhymeWord.lower()):
                return rhyme.lower()

        # the loop exited without breaking, so we found no rhymes that exist in
        # our Markov chains
        return False
    
    def getSynonyms(self, curLine, rhymeLine):
        """Take the previous line we rhymed with and extract synonyms of all
           words it uses. We'll prefer using these words in future lines, so
           the poem has a consistent theme."""
           
        if rhymeLine is False or rhymeLine > (len(self.poem) - 1) or len(self.poem[rhymeLine]) == 0:
            return [] # no rhyming required, or the line has no words
        
        return self.thesaurus.getListSynonyms(map(self.cleanWord, self.poem[rhymeLine]))
    
    def getSynonymWeight(self, word, rhymeLine):
        """Is this word a synonym of one on previous lines?"""
        if len(self.poem) == 0:
            return 0
        
        if word in self.getSynonyms(len(self.poem) - 1, rhymeLine):
            return self.synonymWeight
        
        return 0
    
    def addWords(self, numWords, brain, chain, lines):
        """The challenging part. We query our Markov chain to get the next words possible in
           this line. We then weight the words according to their frequency, synonyms,
           and so on, then choose a word using those weights."""
       
        totalWeight = 0
        
        try:
            rhymeLine = self.getRhymeLine(self.rhymeScheme[len(self.poem) - 1], len(self.poem) - 1)
        except ValueError:
            rhymeLine = False
        
        # try to get the previous words on this line as a seed. if there are none, start a new line
        # (either lines is empty, or it contains the last few words on a line to be completed)
        try:
            seed = lines[-1]
        except IndexError:
            seed = []
            self.poem.append([])

        for i in range(numWords):
            words = self.brains[brain][chain].getNextWords(seed)
            
            if len(words) == 0:
                return 0 # do nothing, we give up
            
            weightedWords = dict()
            for word, num in words.iteritems():
                weightedWords[word] = num * self.frequencyWeight
                weightedWords[word] += self.getSynonymWeight(word, rhymeLine)
            
            # do a weighted random selection from the words
            rand = random.randint(0, sum(weightedWords.values()))
            pos = 0
            for word, weight in weightedWords.items():
                pos += weight
                if rand <= pos:
                    lines[-1].append(word)
                    totalWeight += weight
                    break
        
        return totalWeight
    
    def getLine(self, person, curLine):
        """Pick out some possible lines of poetry. Iterate through and choose the best possible line."""
        
        lines = []
        maxLine = maxWeight = -1
        
        for line in range(0, self.tryLines-1):
            # right, what shall we rhyme with?
            newWord = self.getRhymingWord(curLine, person)
            weight = 0
            
            if newWord is not False:
                # found a rhyme, now put three good words on the end of the line
                lines.append([newWord])
                weight += self.addWords(1, person, "rhy", lines)
                weight += self.addWords(self.lineLen - 2, person, "rev", lines)
                lines[-1].reverse()
            else:
                # found no rhyme, or perhaps this line doesn't need to rhyme.
                lines.append([])
                weight += self.addWords(self.lineLen, person, "fwd", lines)
                
            if weight > maxWeight:
                maxWeight = weight
                maxLine = line
        
        return lines[maxLine]
    
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
            brain['rhy'].close()
        

people = {"b": "bible", "e": "erotica", "c": "carroll", "u": "unabomber", "w": "weeping",
          "j": "ulysses", "l": "legal", "k": "kafka", "t": "twain", "s": "kamasutra",
          "x": "wikisex", "g": "starwars"}

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
    
    sourceDir = "sources/"
    cacheDir = "cache/"
    
    personalities = []
    for personality in list(personality):
        personalities.append(people[personality])
    
    gen = RhymingMarkovGenerator(rhymescheme, personalities, lineLength, sourceDir, cacheDir)
    
    for i in range(numPoems):
        poem = gen.next()
        for line in poem:
            print line
        print ""
    
    gen.close()