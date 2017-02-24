import numpy as np
import os
import re

from cards import Tokenizer
from game import Game
from scipy.spatial.distance import cityblock

"""
Basic stats on dataset
"""

def process_all(data_dir):
    """
    Process all transcripts
    :param data_dir:
    :return:
    """
    # Tokenizer that treats things like '4 H', 'four of hearts',
    # and >:( as single tokens
    tokenizer = Tokenizer()
    vocab = set()
    avg_num_moves = 0.
    avg_num_messages = 0.
    max_num_moves, min_num_moves = 0, 0
    max_num_messages, min_num_messages = 0, 0

    for dir_path, dirnames, filenames in os.walk(data_dir):
        num_transcripts = 0

        for f in filenames:
            # For DS_STORE on MAC
            if not f.startswith("."):
                num_transcripts += 1
                abs_file_path = os.path.join(dir_path, f)
                print abs_file_path
                tokens, num_moves, num_messages = process_transcript(abs_file_path, tokenizer)
                vocab.update(tokens)
                avg_num_moves += num_moves
                avg_num_messages += num_messages
                if num_moves > max_num_moves:
                    max_num_moves = num_moves
                if num_moves < min_num_moves:
                    min_num_moves = num_moves
                if num_messages > max_num_messages:
                    max_num_messages = num_messages
                if num_messages < min_num_messages:
                    min_num_messages = num_messages

    avg_num_moves /= num_transcripts
    avg_num_messages /= num_transcripts

    print "Size of vocab: ", len(vocab)
    print "Avg num moves: ", avg_num_moves
    print "Avg num messages: ", avg_num_messages
    print "Max num moves: ", max_num_moves
    print "Min num moves: ", min_num_moves


def process_transcript(transcript_file, tokenizer):
    """
    Process a single transcript file
    :param transcript_file:
    :param tokenizer:
    :return:
    """
    game = Game(transcript_file)
    tokens = set()
    messages = 0

    for move in game.all_moves:
        if move.message is not None:
            messages += 1
            message = re.sub("--", "", move.message)
            t = tokenizer.tokenize(message)
            tokens.update([tok.lower() for tok in t])

    return tokens, len(game.all_moves), messages


root_dir = os.path.join(os.path.dirname(os.path.abspath(".")), "data/CardsCorpus-v02/transcripts")
process_all(root_dir)