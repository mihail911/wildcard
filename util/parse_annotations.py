import csv
import json
import os
import re

columns = ["P1_HAND", "P2_HAND", "P1_LOC", "P2_LOC",
                "P1_KNOW", "P2_KNOW", "P1_NEED", "P2_NEED", "P1_ABLE", "P2_ABLE",
                "CARD_LOC", "POINTER"]


def categorize_label(speaker, pointer):
    """
    Categorize output of pointer (P1:720) into bins to format for training model
    Right now I bin as follows: (SPEAKER or NONE, ADDRESSEE) -> (0, 1)
    Returns integer from bin above
    :param ex:
    :return:
    """
    # Speaker performs action or utterance is not acted on
    if speaker in pointer or pointer == "NONE" or pointer == "NULL":
        return 0

    # Else addressee performs action as we would like
    return 1


def extract_card(entry):
    """
    Extract card from entry. Expects pattern of form NEED("ax")
    :param entry:
    :return:
    """
    # Try CARD(5H,asdf) pattern
    pattern = r"EXISTS\((.*)\,.*\)"
    m = re.search(pattern, entry)
    if m is None:
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
        for idx, line in enumerate(reader):
            if line[-1] != "" and line[-1].lower() != "pointer":
                print "Good line: ", idx, " ", line[4:]
                ex = parse_line(line)
                print "Ex: ", ex, " COI: ", ex["COI"]
                print "\n"
                utterances.append(ex)

    return utterances


def parse_all(annotation_dir):
    """
    Parse all annotations in dir
    :param annotation_dir:
    :return:
    """
    utterances = []
    for file in os.listdir(annotation_dir):
        if not file.endswith("DS_Store"):
            print "File: ", file
            file_path = os.path.join(annotation_dir, file)
            utterance = parse_annotation_file(file_path)
            utterances.extend(utterance)

    print "Utterances: ", len(utterances)
    return utterances



if __name__ == "__main__":
    annotation_dir = "../data/annotated"
    utterances = parse_all(annotation_dir)



