import csv
import json

titles = ["P1_HAND", "P2_HAND", "P1_LOC", "P2_LOC",
                "P1_KNOW", "P2_KNOW", "P1_NEED", "P2_NEED", "CARD_LOC",
                "POINTER"]


def parse_entry(entry):
    """
    Parse individual entry contained in a column, assumed to be colon separated
    :param entry:
    :return:
    """
    elems = entry.split(";")
    return elems


def parse_file(file_path):
    """
    Parse given file path
    :param file_path:
    :return:
    """
    utterances = []
    with open(file_path) as f:
        reader = csv.reader(f, delimiter=",")
        # Should have 10 columns
        for line in reader:
            print line, len(line)
            # Found utterance of interest
            if line[-1] != "":
                utterance = {}
                relevant = line[4:]
                for title, entry in zip(titles, relevant):
                    elems = parse_entry(entry)
                    utterance[title] = elems

                utterances.append(utterance)

                print "Utterance: ", utterance
    return utterances


if __name__ == "__main__":
    annotations_file = "/Users/mihaileric/Documents/Research/cards/wild-card/data/annotated/cards_0000001_annotated.csv"
    utterance = parse_file(annotations_file)
