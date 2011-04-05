#!/usr/bin/perl

use strict;  # don't suck at perl

my $things = $ARGV[0];
# passing .txt is irrelevant...
$things =~ s/\.txt$//;
my $stuff = $things . ".txt"; # output
$things = $things . "-raw.txt"; # input

# some patterns to split on
my @split_on = (
                 '\. ',
                 '\.\" ',
                 '\.\' ',

                 '\! ',
                 '\!\" ',
                 '\!\' ',

                 '\? ',
                 '\?\" ',
                 '\?\' ',
                 
                 '\.\) +',
                 '\!\) +',
                 '\?\) +',
                 '\.\"\) +'
                            );


# turn things into stuff.
open(STUFF,">$stuff");  open(THINGS,"<$things");

# read file to scalar, kill DOS and real operating system newlines
my $ram_is_cheap = join('', <THINGS>);
$ram_is_cheap =~ s/\r\n/ /g;  $ram_is_cheap =~ s/\n/ /g;

# loop patterns, replace with original pattern plus newline
for my $pattern (@split_on)
{
   # convert escaped pattern back into something readable
   my $initial = $pattern;  $initial =~ s/\\//g;
   $ram_is_cheap =~ s/$pattern/$initial\n/g;
}

print STUFF $ram_is_cheap;

close(THINGS);  close(STUFF);
