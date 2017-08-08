import itertools

from wildcard.util.cards import Tokenizer

"""
Model utilities for calculating features, etc.
"""

MAX_CARD = 13
card_mapping = {"1": 1,
                "2": 2, "3": 3, "4": 4,
                "5": 5, "6": 6, "7": 7,
                "8": 8, "9": 9, "10": 10,
                "J": 11, "Q": 12, "K": 13,
                "A": 1
                }
inverse_mapping = {1: "A", 2: "2", 3: "3", 4: "4", 5: "5",
                   6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
                   11: "J", 12: "Q", 13: "K"}
card_vals = range(1, 14)
all_strategies = [ set([ x if x <= 13 else x - 13 for x in range(y,y+6) ]) for y in range(1,14) ]


def free_hand(hand):
    """
    Return as boolean whether or not a player has available
    space in their hand (i.e. less than 3 cards)
    :param hand: List of cards in hand
    :return: Bool whether player has free space
    """
    return len(hand) < 3


def free_hand_2(hand):
    """
    Return as boolean whether or not a player has available
    space in their hand (i.e. less than 3 of the same suit in a possible
    winning window defined in all_strategies). More complex definition from
    above.
    :param hand: List of cards in hand
    :return:
    """
    if len(hand) < 3:
        return True
    else:
        suits = set( [card.strip()[-1] for card in hand] )  
        #print "suits in hand" , suits 
        if len(suits) > 1:
            return True
        else:
            # get numbers associated 
            card_vals = set([ card_mapping[card.strip()[:-1]] for card in hand ])

            #print "card values" , card_vals
            strategy_found = True
            for strategy in all_strategies:
                if len(strategy.intersection(card_vals)) == 3:
                    strategy_found = False
                    break
            return strategy_found


def compute_window(coi):
    """
    Compute windows of potential straights around given card.
    Note suffixes already stripped off
    :param coi: Card of interest
    :return: Return lists of winnings hands
    """
    card_val = card_mapping[coi]
    windows = []
    for idx, diff in enumerate(range(-6, 0)):
        # Lower bound of card
        lower = card_vals[card_val + diff]
        # Upper bound of card
        upper = card_val + idx
        if upper > MAX_CARD:
            upper -= (MAX_CARD - 1)

        window = []
        # Populate window given ranges defined above
        if lower <= card_val:
            for d in range(card_val - lower):
                window.append(lower + d)
        # coi = 3,  lower = 4, upper = 10
        elif upper >= card_val and upper < lower:
            # Wrap around
            for d in range(1, card_val):
                window.append(d)
            for d in range(lower, MAX_CARD + 1):
                window.append(d)
        else:
            break

        if card_val <= upper:
            for d in range(card_val, upper + 1):
                window.append(d)
        else:
            # Wrap around
            for d in range(card_val, MAX_CARD + 1):
                window.append(d)
            for d in range(1, upper):
                window.append(d)

        windows.append(window)
    return windows


def card_type(coi):
    """
    Extract card type from card ("H", "C", "D", "S")
    :param coi: Card of interest
    :return:
    """
    return coi[-1]


def append_suffix(cards, type):
    appended = []
    for c in cards:
        appended.append(str(c) + type)

    return appended


def compute_ed(hands, coi):
    """
    Compute edit distance for both players given their hands.
    :param hands: "Hands" stores cards for each player in dict:
    {"1":[3H,4H,5H], "2":[6H,7H]}
    :param coi: card-of-interest
    :return:
    """
    type = card_type(coi)
    coi = coi.strip("SDCH")
    windows = compute_window(coi)

    # Clean hands first to clean out empty string
    hands["1"] = [c for c in hands["1"] if c != ""]
    hands["2"] = [c for c in hands["2"] if c != ""]

    all_hands = set(hands["1"] + hands["2"])

    min_ed = float("inf")
    optimal_window = None
    for w in windows:
        w = set(append_suffix(w, type))
        missing = w.difference(all_hands)
        all = w.union(all_hands)

        # Cards over the desired range
        overflow = all.difference(w)

        ed = len(overflow) + len(missing)
        if ed < min_ed:
            min_ed = ed
            optimal_window = w

    # Given optimal window, compute edit distance for each player
    p1_inter = optimal_window.intersection(set(hands["1"]))
    p1_diff = set(hands["1"]).difference(optimal_window)
    p1_edit = 2 * len(p1_diff) + (3 - len(p1_diff) - len(p1_inter))

    p2_inter = optimal_window.intersection(set(hands["2"]))
    p2_diff = set(hands["2"]).difference(optimal_window)
    p2_edit = 2 * len(p2_diff) + (3 - len(p2_diff) - len(p2_inter))

    # Check if all cards in window
    p1_all = True
    for c in hands["1"]:
        if c not in optimal_window:
            p1_all = False

    p2_all = True
    for c in hands["2"]:
        if c not in optimal_window:
            p2_all = False

    return optimal_window, min_ed, p1_edit, p2_edit, [p1_all, p2_all]


def mentions_cards(utterance, tokenizer, card_expressions):
   """
   Return a bool indicating whether the given utterance
   has a mention of a card
   :param utterance: Utterance to parse
   :param tokenizer: Specifies how to parse utterance
   :param card_expressions: Iterable of cards to check for in utterance
   :return: Bool whether any of `card expressions` is contained in utt.
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
   :return: Set of all variants of ways to refer to cards
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


# TODO: Move this to test subdir
if __name__ == "__main__":

    '''
    hand = ["3H", "4H", "5H"]
    #print "Free? ", free_hand(hand)

    hand = ["3H", "4H"]
    #print "Free? ", free_hand(hand)

    hand = ["3H","4H","6S"]
    print "Free? ", free_hand_2(hand)

    hand = ["3H" , "4H" , "10H" ]
    print "Free?" , free_hand_2(hand)
    '''
    print all_strategies

    ######### Test window computation
    # coi = "5"
    # print compute_window(coi)
    # print "-"*10
    #
    # coi = "2"
    # print compute_window(coi)
    # print "-"*10
    #
    # coi = "8"
    # print compute_window(coi)
    # print "-"*10
    #
    # coi = "10"
    # print compute_window(coi)
    # print "-"*10
    #
    # coi = "Q"
    # print compute_window(coi)
    # print "-"*10
    #
    # coi = "K"
    # print compute_window(coi)
    # print "-"*10
    #
    # coi = "A"
    # print compute_window(coi)

    ######## Test edit distance computation
    '''
    coi = "QH"
    hands = {"1": [""], "2": [""]}
    print compute_ed(hands, coi)
    '''

    from game import Game

    transcript = os.path.join(os.path.dirname(os.path.abspath(".")), "data/CardsCorpus-v02/transcripts/01/cards_0000001.csv")
    game = Game(transcript)

    tokenizer = Tokenizer()
    ce = card_expressions()
