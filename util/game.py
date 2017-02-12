import csv
import numpy as np
import os

"""
Stores an instance of a game corresponding to a transcript
"""


class Game(object):

    def __init__(self, transcript):
        # Stores gameboard start, as numpy array of strings
        self.start_gameboard = None

        # Stores running gameboard for reenacting the game
        self.running_gameboard = self.start_gameboard

        # Store all moves in game
        self.all_moves = []
        self.transcript = transcript
        self._process_transcript()


    def _process_transcript(self):
        """
        Processes a transcript and reads the gameboard in appropriately,
        as well as storing all moves made in game
        :return:
        """
        with open(self.transcript) as f:
            file_reader = csv.reader(f)
            raise NotImplementedError


    def step(self, num_moves=1):
        """
        Step the gameboard one move along (i.e. one move of the transcript)
        :param num_moves: Number of moves to step along
        :return:
        """
        raise NotImplementedError


    def __str__(self):
        """
        To be used for printing the current gameboard
        :return:
        """
        return self.transcript


    def reset(self):
        """
        Resets running gameboard to start state
        :return:
        """
        self.running_gameboard = self.gameboard_start


if __name__ == "__main__":
    transcript = os.path.join(os.path.dirname(os.path.abspath(".")), "data/CardsCorpus-v02/transcripts/01/cards_0000001.csv")
    game = Game(transcript)
