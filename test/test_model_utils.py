from wildcard.util.model_utils import compute_ed
from wildcard.util.model_utils import compute_window
from wildcard.util.model_utils import free_hand
from wildcard.util.model_utils import free_hand_2


if __name__ == "__main__":
    # Test window computation
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

    # Free hand
    hand = ["3H", "4H", "5H"]
    #print "Free? ", free_hand(hand)

    hand = ["3H", "4H"]
    #print "Free? ", free_hand(hand)

    hand = ["3H","4H","6S"]
    print "Free? ", free_hand_2(hand)

    hand = ["3H" , "4H" , "10H" ]
    print "Free?" , free_hand_2(hand)

    coi = "QH"
    hands = {"1": [""], "2": [""]}
    print compute_ed(hands, coi)
