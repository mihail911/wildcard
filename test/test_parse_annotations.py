from wildcard.util.parse_annotations import parse_all


if __name__ == "__main__":
    annotation_dir = "../data/annotated"
    utterances = parse_all(annotation_dir)