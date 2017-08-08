#!/usr/bin/env python

"""
A basic tool for working with the Cards corpus transcripts.
"""

__author__ = "Christopher Potts"
__date__ = "2012-03-03"
__credits__ = "Thanks to Karl Schultz for designing the data collecting program, and \
               to David Clausen, Alex Djalali, Sven Lauer, Victoria Schwanda, Chriz Czyzewicz, \
               and the rest of the SUBTLE team for their help with data collection. \
               This research was supported in part by ONR grant No. N00014-10-1-0109 and \
               ARO grant No. W911NF-07-1-0216."
__license__ = "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License: \
               http://creativecommons.org/licenses/by-nc-sa/3.0/"
__version__ = "2.0"
__maintainer__ = "Christopher Potts"
__email__ = "See the author's website"

######################################################################

import re
import os
import sys
import csv
import codecs
import datetime
#import pytz
from glob import iglob

######################################################################
###### ACTIONS CAPTURED BY PRAGBOT TRANSCRIPTS
#
# These variables are useful to have named, and this also serves as a
# reference for the complete list of meta-data values.

# Official names for the two players, as written in the transcripts.
PLAYER1 = "Player 1"
PLAYER2 = "Player 2"

# META-DATA ABOUT THE GAME
ORIGINAL_FILENAME  = r"ORIGINAL_FILENAME"   # Filename as created by the program; included for book-keeping purposes.
COLLECTION_SITE    = r"COLLECTION_SITE"     # 'Amazon Mechanical Turk' or 'Penn'
TASK_COMPLETED     = r"TASK_COMPLETED"      # Completion time - also encode in ORIGINAL_FILENAME
PLAYER             = r"PLAYER_[12]"         # Player Id in the format A[0-9]{5}, else 'UNKNOWN'
P1_MAX_LINEOFSIGHT = r"P1_MAX_LINEOFSIGHT"  # Distance the players could 'see'
P2_MAX_LINEOFSIGHT = r"P2_MAX_LINEOFSIGHT"
ENVIRONMENT        = r"CREATE_ENVIRONMENT"  # ASCII representation of the world
P1_MAX_TURNS       = r"P1_MAX_TURNS"        # Player's maximum allowed turns
P2_MAX_TURNS       = r"P2_MAX_TURNS"
P1_MAX_CARDS       = r"P1_MAX_CARDS"        # Number of cards the player could hold at any given time
P2_MAX_CARDS       = r"P2_MAX_CARDS"
PLAYER_2_TASK_ID   = r"PLAYER_2_TASK_ID"
PLAYER_1_TASK_ID   = r"PLAYER_1_TASK_ID"
GOAL_DESCRIPTION   = r"GOAL_DESCRIPTION"    # High-level goal (always the same in the v1 release)
# ACTIONS
## utterances
UTTERANCE          = r"CHAT_MESSAGE_PREFIX"
## locations
INITIAL_LOCATION   = r"PLAYER_INITIAL_LOCATION"
MOVE               = r"PLAYER_MOVE"
## card movements
PICKUP             = r"PLAYER_PICKUP_CARD"
DROP               = r"PLAYER_DROP_CARD"
# finish
TASK_COMPLETE      = r"TASK_COMPLETE_CLICKED"
CLOSE_SOCKETS      = r"CLOSE_SOCKETS"

######################################################################

class Corpus:
    """
    Corpus instances are built from the directory name of the
    corpus. Thus, if your program is in the same directory as the root
    of the corpus, you can use

    corpus = Corpus('transcripts')

    to build a corpus object.  Relative and full absolute paths also
    work.

    Corpus objects exist mainly as iterators. The methods
    iter_transcripts() and iter_events() allow you to move through the
    entire corpus efficiently.
    """
        
    def __init__(self, dirname):
        """
        Argument:
        dirname -- the root of the corpus transcripts
        """
        self.dirname = dirname

    def iter_transcripts(self, display_progress=True):
        """
        Iterate through the transcripts, by yielding Transcript objects one-by-one.

        Keyword argument:
        display_progress -- should create an overwriting progress bar to stderr if set to True (default: True)        
        """
        trans_no = 1
        for filename in iglob(os.path.join(self.dirname, '*/*.csv')):
            if display_progress:
                sys.stderr.write('\r') ; sys.stderr.write('transcript %s' % trans_no) ; sys.stderr.flush() ; trans_no += 1
            yield Transcript(filename)
        if display_progress:
            sys.stderr.write('\n')

    def iter_events(self, display_progress=True):
        """
        Iterate through the events, by yielding Event objects
        one-by-one.  This is useful if you don't need to rely on the
        transcripts as a unit --- say, because you're just counting
        words for the whole corpus.

        Keyword argument:
        display_progress -- should create an overwriting progress bar to stderr if set to True (default: True)        
        """
        for trans in self.iter_transcripts(display_progress=display_progress):
            for event in trans.iter_events():
                yield event

######################################################################

class Transcript:
    """
    Transcript objects correspond to individual files.
    You can build a Transcript object directly with

    trans = Transcript(filename)

    where filename is the absolute or relative path to the file you
    want to study.
    """
    
    def __init__(self, filename):
        """
        Argument:
        filename -- the source filename

        At intialization, the code turns the filename contents into a
        CSV reader and then turns each row into an Event instance. The
        attribute self.events is an ordered list of those Event
        instances.
        """
        self.filename = filename
        csvreader = csv.reader(codecs.open(self.filename, 'r', 'utf8'))
        self.events = []
        for row in csvreader:                
            self.events.append(Event(row))

    def iter_events(self):
        """
        Iterate through self.events.
        """
        for event in iter(self.events):
            yield event

######################################################################

class Event:
    """
    Events are the basic unit of the corpus. Event objects are not
    really designed to be instantiated directly, but rather only as
    part of a Trancript or Corpus instance. However, you can build
    then directly from a 4-membered list of strings. Here, I've
    copied and pasted a row from one of the CSV files and turned
    it into a list:

    event = Event(['Player 1','4555','PLAYER_INITIAL_LOCATION','16,25']
    """
    def __init__(self, row):
        """
        Argument:
        row -- a row of a csvreader (or a list)

        The attributes created:

        self.agent (str): Server, Player 1, or Player 2

        self.time (int): an integer representing the time of the
                         event relative to the start of the game

        self.action (str): a string capturing the type of action; see the
                           top of this file for details

        self.contents (str): the actual contents of the event; the structure
                             depends on self.action; see self.parse_contents()
                             for details
        """
        self.agent, time, self.action, self.contents = row
        self.time = int(time)

    def parse_contents(self):
        """
        This method seeks to do something useful with the contents of
        the event. Summary:

        -- utterances: return the list of strings as tokenized by Tokenizer().tokenize() [see below]
        -- pickup, drop: return a triple (x-coord, y-coord, card), where the coordinates are the location of the action
        -- move, initial location: return (x-coord, y-coord) of the resulting position
        -- task completed: return parsed date
        -- max cards, max turns, max line-of-sight: return int() of the value
        -- all else: return self.contents
        """
        # Utterances are tokenized using a basic card-aware tokenizer:
        if self.action == UTTERANCE:
            return Tokenizer().tokenize(self.contents)
        # Card manipulations return a trip (x-coord, y-coord, card)
        elif self.action in (PICKUP, DROP):
            loc, card = self.contents.split(":")
            lr, tb = loc.split(",")
            return (int(lr), int(tb), card)
        # Locations: pairs (x-coord, y-coord)
        elif self.action in (MOVE, INITIAL_LOCATION):
            lr, tb = self.contents.split(",")
            return (int(lr), int(tb))
        # Completion times are parsed as dates:
        elif self.action == TASK_COMPLETED:
            time_format = "%Y-%m-%d %H:%M:%S"
            dt = datetime.datetime.strptime(self.contents.replace(' EDT', ''), time_format)
            ##### Uncomment if localization is important:
            # eastern = pytz.timezone('US/Eastern')
            # dt = eastern.localize(dt)
            return dt
        # These values are parsed as integers:
        elif self.action in (P1_MAX_CARDS, P2_MAX_CARDS, P1_MAX_TURNS, P2_MAX_TURNS, P1_MAX_LINEOFSIGHT, P2_MAX_LINEOFSIGHT):
            return int(self.contents)
        # All other values are returned as strings:
        else:
            return self.contents
  
    def __repr__(self):
        """Computable representation of the object."""
        return '[%s]' % ','.join(map((lambda x : '"%s"' % x), (self.agent, self.time, self.action, self.contents)))        

######################################################################    

class Tokenizer:
    """
    This is a very basic tokenizer that seeks to keep intact emoticons
    and card references in a basic way. The class-level variables are
    put into a regular expression word_re (order matters) and then the
    input string is parsed with token_re.findall(). The output list
    treats things like '4 H', 'four of hearts', and >:( as single
    tokens. All characters are retained except whitespace not deemed
    to be word-internal.

    The tokenizer can be used on any string:

    words = Tokenizer().tokenize(s)

    where s is a str or unicode instance. The return value is a list
    of strings or unicode instances.
    """

    # Emoticon identification:
    emoticons = r"""
        (?:
            [<>]?
            [:;=8] # eyes
            [\-o\*\']? # optional nose
            [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth      
            |
            [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
            [\-o\*\']? # optional nose
            [:;=8] # eyes
           [<>]?
        )"""

    # A few final kinds of plain words, and a last resort:
    words = r"""
        (?:[a-zA-Z][a-zA-Z'\-_]+[a-zA-Z]) # Words with apostrophes or dashes.
        |
        (?:[\w_]+)                        # Words without apostrophes or dashes.
        """

    # Ranks:
    ranks = r"""[Tt]wo|[Tt]hree|[Ff]our|[Ff]ive|[Ss]ix|[Ss]even|[Ee]ight|[Nn]ine|[Tt]en|[Jj]ack|[Qq]ueen|[Kk]ing|[Aa]ce
                |
                2|3|4|5|6|7|8|9|10|[Jj]|[Qq]|[Kk]|A"""

    # Suits:
    suits = r"[Hh]earts?|[Dd]iamonds?|[Ss]pades?|[Cc]lubs?|[Hh]|[Ss]|[Dd]|[Cc]"

    # Last-ditch effort to create tokens; finall splits on whitespace:
    misc_punc = r"""
        (?:[+\-]?\d+[,/.:-]\d+[+\-]?)     # Numbers, including fractions, decimals.
        |
        (?:\.(?:\s*\.){1,})               # Ellipsis dots. 
        |
        (?:\S)                            # Everything else that isn't whitespace.
        """

    # The actual tokenizing regular expression:
    token_re = re.compile(r"(%s)" % "|".join((emoticons, words, ranks, suits, misc_punc)), re.VERBOSE)
   
    def tokenize(self, s):
        """
        Tokenize the string s using token_re.findall(). Return value
        is a list of strings or unicode instances.
        """
        return Tokenizer.token_re.findall(s)
