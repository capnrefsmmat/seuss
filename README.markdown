seuss
=====

A Python system for generating rhyming poetry with Markov chains.

Overview
--------

The Rhyming Robot (seuss) uses Markov chains to generate random text. The
chains are generated from analysis of selected source texts placed in the
`sources/` directory -- preferably source texts of 50,000 words or greater.
Each line in a poem can be generated using different source texts, allowing
surprising and amusing combinations (the Bible and legal disclaimers, for
instance).

Markov chains are generated in advance and cached in the `cache/` directory
by makeChains.py. There are three Markov chains used:

 - A forward-looking 2nd-order chain; that is, the next word depends on the
   previous two.
 - A reverse-looking 2nd-order chain
 - A reverse-looking 1st-order chain

The basic process looks like this:

1. The first line of the poem is generated using the forward-looking chain.
2. If the second line does not need to rhyme, it uses the forward chain.
   Otherwise, it uses the rhyming dictionary to find words that rhyme,
   then attempts to find those words in the reverse 1st-order chain.
   This chain is used to find the next-to-last word, and the line is filled in
   in reverse usng the 2nd-order chain after this.
3. Subsequent lines follow the same process, according to the supplied rhyme
   scheme.

Setup
-----

The rhyming dictionary is contained in `data/words.sql.gz`. You'll need to
import this into an SQLite database named `data/sql-words`. To do this, open a
shell in the `data/` directory and type:

```
$ gunzip words.sql.gz
$ sqlite3 sql-words
SQLite version 3.7.13 2012-06-11 02:05:22
Enter ".help" for instructions
Enter SQL statements terminated with a ";"

sqlite> .read words.sql
sqlite> .quit
```

This creates the database and reads the data into it. You're now ready to use
the Rhyming Robot.

Usage
-----

First, supply the robot with a source text. Ideal source texts are very long
(50,000 words or more) and amusing. Choose a source with a normal English
vocabulary -- the rhyming dictionary does not understand specialized terminology
or foreign languages. You may supply as many source texts as you like and switch
between them.

In this example, we will use the World English Bible from ebible.org; use the
plain-text version and put it all in one text file. Cut out any parts you do not
want and save it in `sources/` as `bible-raw.txt`.

Next, run `format.pl` to split the file into sentences:

    $ format.pl bible

`format.pl` will take `name-raw.txt` and transform it into `name.txt`, which
contains the same source with one sentence per line. This can be loaded by the
Markov chain generator.

Heading back up to the directory containing `makeChains.py`, run:

    $ python makeChains.py bible

This may take a long time. Ensure the script has access to the `cache/`
directory and can create files there. Once done, there should be three new
files in `cache/` containing the Markov chains.

Now you'll need to edit the `people` dictionary in `rhyme.py` to know about your
new source. The dictionary maps single characters to source names; you'll use
these characters when choosing what sources will be written in your poem.

You can now write poetry. If you added the Bible with code `b` in the `people`
dictionary, you can specify a rhymescheme `aabba` and personality `bbbbb` to
have the generator use the Bible for every line. The personality specification
must be the same length as the rhymescheme.

Run `python rhyme.py` to see the detailed usage instructions.

IRC Bot
-------

`seuss.py` contains a very simple IRC bot based on twisted.words. It contains
a number of hard-coded configuration parameters; you will have to adjust it
to your needs.

By default, it loads the "brains" (source texts, which must have premade
Markov chains in `cache/`) specified in `self.brains`. `self.chatFraction`
gives the fraction of messages which are responded to by the robot
automatically; the bot will respond to random messages along with any message
that mentions its name.

The server can be specified in the block at the bottom of the file, and the
channel name must be given when the bot is started; e.g.,

    $ python seuss.py channelName

The bot will join any channel it is /invited to, so be wary. It will also
respond to any /msg directed to it; be careful of infinite loops that may
occur when a bot msgs the rhyming bot. (For example, in testing the bot
received a msg from NickServ on connecting, responded, received an "unknown
command" error, responded, etc.) You can use `self.nickExcludeList` to avoid
this issue.

Web Interface
-------------

The web interface is not recommended, as poetry generation can use a 
substantial amount of processing power. Nevertheless, for your amusement,
`poetry.php` is included. Simply place the rhyming robot in a web-accessible
directory and point people to `poetry.php`. Make sure they can't invoke the
Python files from the web, of course. `poetry.php` must be adjusted with a list
of all the valid source texts you have provided.
