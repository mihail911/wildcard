import csv
import json
import numpy as np
import os

"""
Stores an instance of a game corresponding to a transcript
"""

class Move(object):

    def __init__(self, player, move_type, data):
        if player == "Player 1":
            self.player = 1
        else:
            self.player = 2

        self.move_type = move_type

        if move_type == "PLAYER_MOVE":
            self.coords = [int(c) for c in data.split(",")]
            self.card = None
            self.message = None
        elif move_type == "PLAYER_PICKUP_CARD" or move_type == "PLAYER_DROP_CARD":
            x, rest = data.split(",")
            y, card = rest.split(":")
            self.coords = [int(x), int(y)]
            self.card = card
            self.message = None
        elif move_type == "CHAT_MESSAGE_PREFIX":
            self.coords, self.card = None, None
            self.message = data
        else:
            self.coords, self.card, self.message = None, None, None


    @property
    def _data_str(self):
        data = ""
        if self.coords is not None:
            data += str(self.coords)
        if self.card is not None:
            data += "," + self.card
        if self.message is not None:
            data += self.message

        return data


    def __str__(self):
        # Returns json string
        return json.dumps([self.player, self.move_type, self._data_str])



class Game(object):

    def __init__(self, transcript):
        # Stores gameboard start, as numpy array of strings
        self.start_gameboard = None
        # Stores various parameters about the current game
        self.game_config = {}

        # Stores running gameboard for reenacting the game
        self.running_gameboard = self.start_gameboard

        # Store all moves in game
        self.all_moves = []
        self.transcript = transcript
        self._process_transcript()


    def _recreate_start_gameboard(self, gameboard_str):
        """
        Recreate start of gameboard by processing gameboard str
        from CREATE_ENVIRONMENT line in transcript
        :param gameboard_str:
        :return:
        """
        
        gameboard_str = gameboard_str.split( ";" )
        board_rows = []
        rows = []

        # separate out the layout of walls from the distribution of cards
        start = None
        for i,row in enumerate(game_string):
            if not row.startswith( "NEW_SECTION" ):
            rows.append( row )
        else:
            start = i
            break

        # recreate board as a numpy array of ones and zeros
        gameboard=np.array([ [ 1 if (char == "-" or char == "b") else 0 for char in row ] for row in rows ])

        # now get card positions from the rest of the entries
        card_positions = {}
        for elem in gameboard_str[ start : ]: 
            if elem: # make sure elem is non-empty
                position,card=elem.strip( "NEW_SECTION" ).split( ":" )
                row,col=position.split(",")
                positions[ (int(row),int(col)) ] = card

        ## not sure what kind of instance variables we want to store
        self.gameboard = gameboard
        self.initial_card_positions = card_positions



    def _process_transcript(self):
        """
        Processes a transcript and reads the gameboard in appropriately,
        as well as storing all moves made in game
        :return:
        """
        with open(self.transcript) as f:
            file_reader = csv.reader(f)
            for line in file_reader:
                if line[2] == "CREATE_ENVIRONMENT":
                    self._recreate_start_gameboard(line[3])
                elif line[2] == "P1_MAX_CARDS":
                    self.game_config["p1_max_cards"] = int(line[3])
                elif line[2] == "P2_MAX_CARDS":
                    self.game_config["p2_max_cards"] = int(line[3])
                elif line[2] == "P1_MAX_TURNS":
                    self.game_config["p1_max_turns"] = int(line[3])
                elif line[2] == "P2_MAX_TURNS":
                    self.game_config["p2_max_turns"] = int(line[3])
                elif line[2] == "PLAYER_INITIAL_LOCATION" and line[0] == "Player 1":
                    self.game_config["p1_initial_location"] = [int(c) for c in line[3].split(",")]
                elif line[2] == "PLAYER_INITIAL_LOCATION" and line[0] == "Player 2":
                    self.game_config["p2_initial_location"] = [int(c) for c in line[3].split(",")]
                # Handle remaining moves, disregarding metadata
                elif line[2] not in ["ORIGINAL_FILENAME", "COLLECTION_SITE", "TASK_COMPLETED",
                                     "PLAYER_1", "PLAYER_2", "PLAYER_1_TASK_ID", "PLAYER_2_TASK_ID", "GOAL_DESCRIPTION"]:
                    move = Move(line[0], line[2], line[3])
                    self.all_moves.append(move)


    def step(self, num_moves=1):
        """
        Step the gameboard one move along (i.e. one move of the transcript)
        :param num_moves: Number of moves to step along
        :return:
        """
        raise NotImplementedError


    def reset(self):
        """
        Resets running gameboard to start state
        :return:
        """
        self.running_gameboard = self.gameboard_start


    def __str__(self):
        """
        To be used for printing the current gameboard
        :return:
        """
        return self.transcript





if __name__ == "__main__":
    transcript = os.path.join(os.path.dirname(os.path.abspath(".")), "data/CardsCorpus-v02/transcripts/01/cards_0000001.csv")
    game = Game(transcript)

    m1 = Move("Player 1", "PLAYER_MOVE", "8,10")
    m2 = Move("Player 2", "CHAT_MESSAGE_PREFIX", "hi there10")
    m3 = Move("Player 2", "PLAYER_PICKUP_CARD", "16,14:4H")
