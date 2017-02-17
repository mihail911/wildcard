import copy
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
            self.coords, self.card, self.message = None, None, "TASK_COMPLETE_CLICKED"


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

        # Store cards that each player has in hands
        # TODO: Create Player objects storing this information as well
        # as state
        self.p1_cards, self.p2_cards = [], []
        self.p1_loc = self.game_config["p1_initial_location"]
        self.p2_loc = self.game_config["p2_initial_location"]


    def _recreate_start_gameboard(self, gameboard_str):
        """
        Recreate start of gameboard by processing gameboard str
        from CREATE_ENVIRONMENT line in transcript
        :param gameboard_str:
        :return:
        """
        
        gameboard_str = gameboard_str.split( ";" )
        rows = []

        # separate out the layout of walls from the distribution of cards
        start = None
        for i,row in enumerate(gameboard_str):
            if not row.startswith( "NEW_SECTION" ):
                rows.append( row )
            else:
                start = i
                break

        # recreate board as a numpy array of ones and zeros
        # TODO: Should we represent hidden walls distinctly from regular walls?
        # TODO: Change to -1 for hidden walls
        gameboard = []
        for row in rows:
            row_rep = []
            for char in row:
                if char == "-":
                    row_rep.append(1)
                elif char == "b":
                    row_rep.append(-1)
                else:
                    row_rep.append(0)
            gameboard.append(row_rep)
        # Convert to numpy array
        gameboard = np.array(gameboard, dtype=object)

        # now get card positions from the rest of the entries
        position_to_card = {}
        card_to_position = {}
        for elem in gameboard_str[ start: ]:
            if elem: # make sure elem is non-empty
                if elem.startswith("NEW_SECTION"):
                    elem = elem.strip("NEW_SECTION")
                position, card = elem.split( ":" )
                row, col = position.split(",")
                position_to_card[ (int(row),int(col)) ] = card
                card_to_position[card] = (int(row), int(col))


        self.start_gameboard = gameboard
        self.positon_to_card = position_to_card
        self.card_to_position = card_to_position


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
                    self.start_gameboard[self.game_config["p1_initial_location"][0],
                                         self.game_config["p1_initial_location"][1]] = "P1"
                elif line[2] == "PLAYER_INITIAL_LOCATION" and line[0] == "Player 2":
                    self.game_config["p2_initial_location"] = [int(c) for c in line[3].split(",")]
                    self.start_gameboard[self.game_config["p2_initial_location"][0],
                                         self.game_config["p2_initial_location"][1]] = "P2"
                # Handle remaining moves, disregarding metadata
                elif line[2] not in ["ORIGINAL_FILENAME", "COLLECTION_SITE", "TASK_COMPLETED",
                                     "PLAYER_1", "PLAYER_2", "PLAYER_1_TASK_ID", "PLAYER_2_TASK_ID", "GOAL_DESCRIPTION"]:
                    move = Move(line[0], line[2], line[3])
                    self.all_moves.append(move)


    def step(self, num_moves=1):
        """
        Step the gameboard one move along (i.e. one move of the transcript) from
        start gameboard state
        :param num_moves: Number of moves to step along
        :return:
        """
        running_gameboard = copy.deepcopy(self.start_gameboard)

        for idx in range(num_moves):
            move = self.all_moves[idx]
            print move
            if move.move_type == "PLAYER_MOVE":
                coords = move.coords
                if move.player == 1:
                    running_gameboard[coords[0], coords[1]] = "P1"
                    old_loc = self.p1_loc
                    running_gameboard[old_loc[0], old_loc[1]] = 0
                    self.p1_loc = coords
                elif move.player == 2:
                    running_gameboard[coords[0], coords[1]] = "P2"
                    old_loc = self.p2_loc
                    running_gameboard[old_loc[0], old_loc[1]] = 0
                    self.p2_loc = coords
            elif move.move_type == "PLAYER_PICKUP_CARD":
                coords = move.coords
                if move.player == 1:
                    self.p1_cards.append(move.card)
                elif move.player == 2:
                    self.p2_cards.append(move.card)

                del self.card_to_position[move.card]
                del self.position_to_card[coords[0], coords[1]]
            elif move.move_type == "PLAYER_DROP_CARD":
                coords = move.coords
                if move.player == 1:
                    try:
                        self.p1_cards.remove(move.card)
                    except Exception as e:
                        print e
                elif move.player == 2:
                    try:
                        self.p2_cards.remove(move.card)
                    except Exception as e:
                        print e
                self.card_to_position[move.card] = tuple(coords)
                self.position_to_card[coords[0], coords[1]] = move.card


        return running_gameboard


    def reset(self):
        """
        Resets running gameboard to start state
        :return:
        """
        self.running_gameboard = self.gameboard_start


    def make_heatmap(self):
        """
        Make a heatmap for the gameboard by keeping counts of which squares have been
        visited a set number of times over the course of the game
        :return:
        """
        raise NotImplementedError


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

    game.step(1)
