import random

from wildcard.util.parse_annotations import parse_all

"""
Variety of utils for preparing data for model
"""

random.seed(42)

def split_data(utterances, split=[0.8, 0.2]):
    """
    Split data into train/test according to provided ratio
    :param split: Split to use for train/test
    :return:
    """
    random.shuffle(utterances)
    bound = int(len(utterances) * split[0])
    train = utterances[:bound]
    test = utterances[bound:]
    return train, test
