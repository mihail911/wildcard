"""
Model utilities for calculating features, etc.
"""

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
MAX_CARD = 13


def free_hand(hand):
    """
    Return as boolean whether or not a player has available
    space in their hand (i.e. less than 3 cards)
    :param hand:
    :return:
    """
    return len(hand) < 3


def compute_window(coi):
    """
    Compute windows of potential straights around given card.
    Note suffixes already stripped off
    :param coi:
    :return:
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


def compute_ed(hands, coi):
    """
    Compute edit distance for both players given their hands.
    "Hands" stores cards for each player in dict: {"1":[3H,4H,5H], "2":[6H,7H]}
    :param hands:
    :param coi: card-of-interest
    :return:
    """
    suffixes = ["H", "C", "D", "S"]


if __name__ == "__main__":
    hand = ["3H", "4H", "5H"]
    print "Free? ", free_hand(hand)

    hand = ["3H", "4H"]
    print "Free? ", free_hand(hand)


    coi = "5"
    print compute_window(coi)
    print "-"*10

    coi = "2"
    print compute_window(coi)
    print "-"*10

    coi = "8"
    print compute_window(coi)
    print "-"*10

    coi = "10"
    print compute_window(coi)
    print "-"*10

    coi = "Q"
    print compute_window(coi)
    print "-"*10

    coi = "K"
    print compute_window(coi)
    print "-"*10

    coi = "A"
    print compute_window(coi)

