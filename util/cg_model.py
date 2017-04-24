import numpy as np
import os

from collections import Counter
from data_util import split_data
from model_util import free_hand, compute_ed
from parse_annotations import parse_all
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_recall_curve, roc_curve
from sklearn.svm import SVC

"""
Model for using common ground annotations to
predict player actions
"""


class CGModel(object):
    """
    Model that uses common ground to predict player actions
    """
    def __init__(self):
        self.classifier = LogisticRegression()


    def _featurize(self, data):
        """
        Featurize data
        :param data:
        :return:
        """
        x, y = [], []
        for d in data:
            ex = {}
            hands = {"1": d["P1_HAND"], "2": d["P2_HAND"]}
            coi = d["COI"]
            _, ed, p1_ed, p2_ed = compute_ed(hands, coi)

            # TODO: Include feature for mention of strategy?

            if d["SPEAKER"] == "P1":
                # Indicator function that addressee edit smaller than speaker
                if p2_ed < p1_ed:
                    ex["ADDRESSEE_EDIT"] = 1.

                # Check if speaker/addressee have available space
                if free_hand(d["P1_HAND"]):
                    ex["SPEAKER_FREE"] = 1.
                if free_hand(d["P2_HAND"]):
                    ex["ADDRESSEE_FREE"] = 1.
            else:
                if p1_ed < p2_ed:
                    ex["ADDRESSEE_EDIT"] = 1.

                if free_hand(d["P2_HAND"]):
                    ex["SPEAKER_FREE"] = 1.
                if free_hand(d["P1_HAND"]):
                    ex["ADDRESSEE_FREE"] = 1.

            label = d["POINTER"]

            x.append(ex)
            y.append(label)

        return x, y


    def train(self, data):
        """
        Train model
        :return:
        """
        x, y = self._featurize(data)
        self.feature_vectorizer = DictVectorizer()

        # Feature vectors converted to matrix  (num_samples, num_features)
        feature_vec_transform = self.feature_vectorizer.fit_transform(x)
        self.classifier.fit(feature_vec_transform, np.array(y))


    def predict(self, x):
        """
        Provide features for a given group as a dict
        :param data:
        :return:
        """
        # Transform features to appropriate format
        features_transformed = self.feature_vectorizer.transform(x)
        y_scores = self.classifier.predict_proba(features_transformed)
        y_scores = [y[1] for y in y_scores]
        return self.classifier.predict(features_transformed), y_scores


    def evaluate(self, test_data):
        """
        Test model
        :return:
        """
        x, gold_labels = self._featurize(test_data)
        predicted_labels, y_scores = self.predict(x)
        accuracy = accuracy_score(gold_labels, predicted_labels)
        recall = recall_score(gold_labels, predicted_labels)
        f1 = f1_score(gold_labels, predicted_labels)

        print "Accuracy: {0}, Recall: {1}, F1: {2}".format(accuracy,
                                                    recall, f1)



if __name__ == "__main__":
    annotation_dir = "/Users/mihaileric/Documents/Research/cards/wild-card/data/annotated"
    utterances = parse_all(annotation_dir)
    train_data, test_data = split_data(utterances)
    model = CGModel()
    model.train(train_data)
    model.evaluate(test_data)
