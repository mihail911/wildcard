from wildcard.model.cg_model import CGModel
from wildcard.util.parse_annotations import parse_all
from wildcard.util.data_utils import split_data


if __name__ == "__main__":
    annotation_dir = "../data/annotations_reworked"
    utterances = parse_all(annotation_dir)
    train_data, test_data = split_data(utterances)
    model = CGModel()
    model.train(train_data)
    model.evaluate(test_data)