from parse_annotations import parse_all

"""
Variety of utils for preparing data for model
"""

def split_data(utterances, split=[0.9, 0.1]):
    """
    Split data into train/test according to provided ratio
    :param split:
    :return:
    """
    bound = int(len(utterances) * split[0])
    train = utterances[:bound]
    test = utterances[bound:]
    return train, test


if __name__ == "__main__":
    annotation_dir = "/Users/mihaileric/Documents/Research/cards/wild-card/data/annotated"
    utterances = parse_all(annotation_dir)
    train_data, test_data = split_data(utterances)

    print "Train: ", train_data
    print "Test: ", test_data
