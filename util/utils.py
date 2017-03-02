import itertools
import os
import re

from cards import Tokenizer



class Color:
   """
   Basic utility for colored printing
   """
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   END = '\033[0m'

   color_map = {"green": GREEN,
                "yellow": YELLOW,
                "red": RED,
                }

   def color_str(self, str, color="green"):
      return Color.color_map[color] + str + Color.END


def mentions_cards(utterance, tokenizer, card_expressions):
   """
   Return a bool indicating whether the given utterance
   has a mention of a card
   :param utterance:
   :return:
   """
   tokens = set(tokenizer.tokenize(utterance.lower()))
   for c in card_expressions:
      if c in tokens:
         contains_cref = True
         return contains_cref

   return False


def card_expressions():
   """
   Set of all possible card referring expressions
   :return:
   """
   card_numbers = ["two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "jack", "queen", "king", "ace"]
   card_combinations = []
   for i, j in itertools.product([2, 3, 4, 5, 6, 7, 8, 9, 10, "j", "q", "k", "a"], ["h", "s", "d", "c"]):
      card_combinations.append(str(i) + str(j))
      card_combinations.append(str(j) + str(i))

   card_suits = []
   for suit in ["heart", "diamond", "spade", "club"]:
      card_suits.append(suit)
      card_suits.append(suit + "s")

   return set(card_numbers + card_combinations + card_suits)


if __name__ == "__main__":
   from game import Game

   transcript = os.path.join(os.path.dirname(os.path.abspath(".")), "data/CardsCorpus-v02/transcripts/01/cards_0000001.csv")
   game = Game(transcript)

   tokenizer = Tokenizer()
   ce = card_expressions()
