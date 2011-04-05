#!/usr/bin/python
"""
Generate Markov chains to be cached in the filesystem; this saves us the effort
of generating new chains every time we want to make poetry.
"""

import sys, Markov, glob, os

def makeChain(name, sourceDir, cacheDir):
    """Parse the source text to generate new Markov chains."""
    sourceFile = sourceDir + name + ".txt"
    
    fwd = Markov.MarkovChain(cacheDir + name + "-fwd", 2, True)
    rev = Markov.MarkovChain(cacheDir + name + "-rev", 2, True)
    rhy = Markov.MarkovChain(cacheDir + name + "-rhy", 1, True)
    
    try:
        for line in open(sourceFile):
            words = line.split()
            if len(words) > 0:
                fwd.add(words)
                words.reverse()     # the rest of the chains work in reverse
                rev.add(words)
                rhy.add(words)
    except IOError:
        print "The source named '%s' does not exist" % (name,)
    finally:
        fwd.close()
        rev.close()
        rhy.close()

def deleteChainCache(name, cacheDir):
    """Delete the old cached versions of the chains, so we start fresh rather than adding
       to the previous chain files."""
    try:
        os.remove(cacheDir + name + "-fwd")
        os.remove(cacheDir + name + "-rev")
        os.remove(cacheDir + name + "-rhy")
    except OSError:
        # if they don't exist, we don't care
        pass
    

if __name__ == "__main__":         
    if len(sys.argv) < 2:
        print """Usage:
    makeChains.py chainName
where chainName is a specific source text to parse and cache."""
        sys.exit(1)
    
    print "Deleting old cache files"
    deleteChainCache(sys.argv[1], "cache/")
    
    print "Creating new cache files"
    makeChain(sys.argv[1], "sources/", "cache/")
    
    print "Chain(s) created successfully."