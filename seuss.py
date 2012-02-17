#!/usr/bin/python

import rhyme, sys, re, random

from twisted.words.protocols import irc
from twisted.internet import protocol
from twisted.internet import reactor


class SeussBot(irc.IRCClient):
    def __init__(self):
        self.chatFraction = 0.010 # fraction of messages we respond to in rhyme
        self.brains = ['erotica', 'weeping', 'wikisex', 'fanny-hill']
        self.gen = rhyme.RhymingMarkovGenerator('a' * len(self.brains),
                                                self.brains, 10, "cache/")
        self.nickExcludeList = ['ChanServ', 'NickServ', 'Global']
        
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def signedOn(self):
        self.msg("NickServ", "identify password")
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)

    def joined(self, channel):
        print "Joined %s." % (channel,)

    def privmsg(self, user, channel, msg):
        if not user:
            return
        
        if channel == self.nickname:
            user = user.split('!', 1)[0]
            channel = user
            
            if user in self.nickExcludeList:
                return

            if user == 'Capn_Refsmmat':
                if msg.startswith('say'):
                    msg = msg.split(' ', 2)
                    self.msg(msg[1], msg[2])
                    print "Speaking on command in %s: '%s'" % (msg[1], msg[2])
                    return
                
                if msg.startswith('rhyme'):
                    msg = msg.split(' ', 2)
                    channel = msg[1]
                    msg = msg[2]
                    print "Rhyming on command in %s: '%s'" % (channel, msg)

                if msg.startswith('act'):
                    msg = msg.split(' ', 2)
                    self.describe(msg[1], msg[2].strip())
                    print "Acting on command in %s: '%s'" % (msg[1], msg[2])
                    return
            
            prefix = True
        elif self.nickname in msg.lower():
            msg = re.compile(self.nickname + "[:,]* ?", re.I).sub('', msg)
            prefix = "%s: " % (user.split('!', 1)[0], )
        else:
            prefix = ''
        
        if prefix or random.random() <= self.chatFraction:
            self.gen.poem = [msg,]
            line = self.gen.getLine(random.choice(self.brains), 1)
            if len(line) == 0:
                return
            line[-1] = self.gen.cleanWord(line[-1])
            rhyme = " ".join(line) + random.choice(['!', '?', '.'])
            self.msg(channel, str(rhyme))
            print "%s: '%s'" % (channel, rhyme) 

    # don't reply to automated messages!    
    def noticed(self, user, channel, message):
        pass

    def action(self, user, channel, msg):
        self.privmsg(user, channel, msg)
    
    def irc_INVITE(self, prefix, params):
       # well, we've been invited to params[1]...
       self.join(params[1])


class SeussBotFactory(protocol.ClientFactory):
    protocol = SeussBot

    def __init__(self, channel, nickname='seuss'):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)


if __name__ == "__main__":
    chan = sys.argv[1]
    reactor.connectTCP('phoenix.xyloid.org', 6667, SeussBotFactory('#' + chan))
    reactor.run()
