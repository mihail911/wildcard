import numpy as np
import os
import random

from collections import Counter
from data_util import split_data
from model_util import free_hand, compute_ed
from parse_annotations import parse_all, extract_card
from sklearn import tree
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_recall_curve, roc_curve, \
                            confusion_matrix
from sklearn.pipeline import FeatureUnion
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
        self.feature_union = FeatureUnion([("count", CountVectorizer()),
                                           ("feat", DictVectorizer())])


    def _featurize(self, data):
        """
        Featurize data
        :param data:
        :return:
        """
        x, x_text, y = [], [], []
        for d in data:
            ex = {}
            hands = {"1": d["P1_HAND"], "2": d["P2_HAND"]}
            coi = d["COI"]
            window, ed, p1_ed, p2_ed, c_all = compute_ed(hands, coi)

            # Mentioned strategy
            # if len(d["P1_NEED"]) > 0 or len(d["P2_NEED"]) > 0:
            #     ex["MENTIONED_STRATEGY"] = 1.

            # More fine-grained feature for card mentioned in strategy
            all_needed = d["P1_NEED"] + d["P2_NEED"]
            all_needed = [extract_card(n) for n in all_needed]
            mentioned = False
            for c in all_needed:
                if c == d["COI"]:
                    mentioned = True
                # Wild card suit
                if c[0] == "X":
                    if c[1] == d["COI"][-1]:
                        mentioned = True

            if mentioned:
                ex["SPECIFIC_STRATEGY"] = 1.

            # if d["SPEAKER"] == "P1":
            #     # Indicator function that addressee edit smaller than speaker
            #     # if p2_ed < p1_ed:
            #     #     ex["ADDRESSEE_EDIT"] = 1.
            #     # if c_all[0]:
            #     #     print "HERE"
            #     #     ex["A_SHOULD_ACT"] = 1.
            #     # if free_hand(hands["2"]):
            #     #     ex["FREE"] = 1.
            #
            # else:
            #     # if p1_ed < p2_ed:
            #     #     ex["ADDRESSEE_EDIT"] = 1.
            #     # if c_all[1]:
            #     #     print "HERE"
            #     #     ex["A_SHOULD_ACT"] = 1.
            #     # if free_hand(hands["1"]):
            #     #     ex["FREE"] = 1.

            extra = window.intersection(hands["1"] + hands["2"])

            if len(extra) == 0:
                ex["WINDOW"] = 1.

            # if p1_ed + p2_ed < 3:
            #     ex["EDIT"] = 1.
            label = d["POINTER"]

            x_text.append(d["DIALOGUE"])
            x.append(ex)
            y.append(label)

        print "COUNTS: ", Counter(y)
        return x, x_text, y


    def train(self, data):
        """
        Train model
        :return:
        """
        x, x_text, y = self._featurize(data)
        # Positive prior for class distribution
        self.positive_prior = sum([1. for _ in y if _ == 1.]) / len(y)

        self.feature_vectorizer = DictVectorizer()
        # self.count_vectorizer = CountVectorizer(ngram_range=(1,2))

        # Feature vectors converted to matrix  (num_samples, num_features)
        feature_vec_transform = self.feature_vectorizer.fit_transform(x)
        #count_vec_transform = self.count_vectorizer.fit_transform(x_text)

        #self.classifier.fit(feature_vec_transform, np.array(y))
        self.classifier.fit(feature_vec_transform, np.array(y))


    def predict(self, x, x_text):
        """
        Provide features for a given group as a dict
        :param data:
        :return:
        """
        # Transform features to appropriate format
        features_transformed = self.feature_vectorizer.transform(x)
        #count_vec_transformed = self.count_vectorizer.transform(x_text)

        y_scores = None
        y_scores = self.classifier.predict_proba(features_transformed)
        y_scores = [y[1] for y in y_scores]

        # Scores using unigram features
        y_scores_uni = None
        # y_scores_uni = self.classifier.predict_proba(count_vec_transformed)
        # y_scores_uni = [y[1] for y in y_scores_uni]

        return self.classifier.predict(features_transformed), y_scores, y_scores_uni


    def evaluate(self, test_data):
        """
        Test model
        :return:
        """
        x, x_text, gold_labels = self._featurize(test_data)
        predicted_labels, y_scores, y_scores_uni = self.predict(x, x_text)

        baseline_labels = []
        # baseline
        for _ in range(len(gold_labels)):
            if random.random() < self.positive_prior:
                baseline_labels.append(1)
            else:
                baseline_labels.append(0)
        baseline_accuracy = accuracy_score(gold_labels, baseline_labels)
        baseline_recall = recall_score(gold_labels, baseline_labels)
        baseline_f1 = f1_score(gold_labels, baseline_labels)

        maj_labels = [1. for _ in range(len(baseline_labels))]
        maj_accuracy = accuracy_score(gold_labels, maj_labels)
        maj_recall = recall_score(gold_labels, maj_labels)
        maj_f1 = f1_score(gold_labels, maj_labels)

        accuracy = accuracy_score(gold_labels, predicted_labels)
        recall = recall_score(gold_labels, predicted_labels)
        f1 = f1_score(gold_labels, predicted_labels)

        print "Accuracy: {0}, Recall: {1}, F1: {2}".format(accuracy,
                                                    recall, f1)
        print "Confusion Matrix: ", confusion_matrix(gold_labels, predicted_labels)

        print "=" * 10
        print "Random Baseline Accuracy: {0}, Recall: {1}, F1: {2}".format(baseline_accuracy,
                                                    baseline_recall, baseline_f1)
        print "Random Baseline Confusion Matrix: ", confusion_matrix(gold_labels, baseline_labels)

        print "=" * 10
        print "Maj Baseline Accuracy: {0}, Recall: {1}, F1: {2}".format(maj_accuracy,
                                                    maj_recall, maj_f1)
        print "Maj Baseline Confusion Matrix: ", confusion_matrix(gold_labels, maj_labels)



if __name__ == "__main__":
    annotation_dir = "../data/annotated"
    utterances = parse_all(annotation_dir)
    train_data, test_data = split_data(utterances)
    model = CGModel()
    model.train(train_data)
    model.evaluate(test_data)
