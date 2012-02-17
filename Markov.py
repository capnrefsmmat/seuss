import random, shelve

class MarkovChain:
	start = "[START!*]"
	
	def __init__(self, chainPath, level = 2, wb = False):
		"""chainPath is the location of the Markov chain to load; wb is
		for Shelve's writeback option. If writeback is set to true, 
		Shelve will keep track of all changes to the chains and save 
		them when closed. We don't need this during normal operation."""
		self.level = level
		self.chain = shelve.open(chainPath, protocol = 2, 
					 writeback = wb)
	
	def add(self, iterable):
		""" Insert an iterable (pattern) item into the Markov chain.
			The order of the pattern will define more of the chain.
		"""
		prefix = [self.start] * self.level
		for item in iterable:
			key = " ".join(prefix)
			if not key in self.chain:
				self.chain[key] = dict()
			
			if item in self.chain[key]:
				self.chain[key][item] += 1
			else:
				self.chain[key][item] = 1
			
			prefix.append(item)
			prefix.pop(0)
	
	def getNextWords(self, line):
		""" Get the next words possible in our chain."""
		
		# if we're at the beginning of the line, pad with start sequence
		if len(line) < self.level:
			line = [self.start] * (self.level - len(line)) + line
		
		key = str(" ".join(line[-self.level:]))
		
		if key in self.chain:
			return self.chain[key]
		else:
			return []
	
	def close(self):
		self.chain.close()
