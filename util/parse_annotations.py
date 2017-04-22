import csv
import json
import re

columns = ["P1_HAND", "P2_HAND", "P1_LOC", "P2_LOC",
                "P1_KNOW", "P2_KNOW", "P1_NEED", "P2_NEED", "P1_ABLE", "P2_ABLE",
                "CARD_LOC", "POINTER"]


def categorize_label(speaker, pointer):
    """
    Categorize output of pointer (P1:720) into bins to format for training model
    Right now I bin as follows: (SPEAKER, ADDRESSEE, NONE) -> (0, 1, 2)
    Returns integer from bin above
    :param ex:
    :return:
    """
    if pointer == "NONE":
        return 2
    # Speaker performs action
    if speaker in pointer:
        return 0
    # Addressee performs action
    else:
        return 1


def extract_card(entry):
    """
    Extract card from entry. Expects pattern of form NEED("ax")
    :param entry:
    :return:
    """
    pattern = r"EXISTS\((.*)\)"
    m = re.search(pattern, entry)
    return m.group(1)


def parse_line(line):
    """
    Parse line, represented as list
    :param entry:
    :return:
    """
    ex = {}
    speaker = line[0]
    # Remember to put speaker in example so we know how to categorize output later
    if "1" in speaker:
        ex["SPEAKER"] = "P1"
    else:
        ex["SPEAKER"] = "P2"

    for col, val in zip(columns, line[4:]):
        # Convert cards in hand into list
        if col.endswith("HAND"):
            hand = val.split(";")
            ex[col] = hand
        elif col.endswith("KNOW") or col.endswith("NEED"):
            entries = val.split(";")
            entries = [e.strip() for e in entries]
            ex[col] = entries
        elif col == "POINTER":
            label = categorize_label(ex["SPEAKER"], val)
            ex[col] = label
        else:
            ex[col] = val

    # Extract card of interest --> Right now convention is that first
    # entry in speaker "KNOW" list is the card of interest
    if ex["SPEAKER"] == "P1":
        coi = extract_card(ex["P1_KNOW"][0])
    else:
        coi = extract_card(ex["P2_KNOW"][0])
    ex["COI"] = coi

    return ex


def parse_annotation_file(file_path):
    """
    Parse given annotation file path
    :param file_path:
    :return:
    """
    utterances = []
    with open(file_path) as f:
        reader = csv.reader(f, delimiter=",")
        # Should have 14 columns
        for line in reader:
            if line[-1] != "":
                print "Good line: ", line[4:]
                ex = parse_line(line)
                print "Ex: ", ex
                print "\n"
                utterances.append(ex)

    return utterances


if __name__ == "__main__":
    annotation_file_1 = "/Users/mihaileric/Documents/Research/cards/wild-card/data/annotated/cards_0000031_annotated.csv"
    utterance = parse_annotation_file(annotation_file_1)

    annotation_file_2 = "/Users/mihaileric/Documents/Research/cards/wild-card/data/annotated/cards_0000001_annotated.csv"
    utterance = parse_annotation_file(annotation_file_2)

    # annotation_file_3 = "/Users/mihaileric/Documents/Research/cards/wild-card/data/annotated/cards_0000031_annotated.csv"
    # utterance = parse_annotation_file(annotation_file_3)

