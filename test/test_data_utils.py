from wildcard.util.data_utils import parse_all
from wildcard.util.data_utils import split_data

if __name__ == "__main__":
    annotation_dir = "../data/annotated"
    utterances = parse_all(annotation_dir)
    train_data, test_data = split_data(utterances)

    print "Train: ", train_data
    print "Test: ", test_data