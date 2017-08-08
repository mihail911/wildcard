import numpy as np
import os
import random

from collections import Counter
from wildcard.util.data_utils import split_data
from wildcard.util.model_utils import compute_ed
from wildcard.util.model_utils import free_hand
from wildcard.util.model_utils import free_hand_2
from wildcard.util.parse_annotations import extract_card
from wildcard.util.parse_annotations import parse_all
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_recall_curve, roc_curve, \
                            confusion_matrix
from sklearn.pipeline import FeatureUnion
from sklearn.svm import SVC
from sklearn import tree

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
        for k, d in enumerate(data):

            ex = {}
            hands = {"1": d["P1_HAND"], "2": d["P2_HAND"]}
            coi = d["COI"]
            window, ed, p1_ed, p2_ed, c_all = compute_ed(hands, coi)

            ## HAND IMBALANCE FEATURE 
            full_speaker_hand = None
            full_addressee_hand = None
            if d["SPEAKER"] == "P1":
                full_speaker_hand = 1 if not free_hand_2(hands["1"])  else 0
                full_addressee_hand = 1 if not free_hand_2(hands["2"]) else 0 
            else:
                full_speaker_hand = 1 if not free_hand_2(hands["2"]) else 0
                full_addressee_hand = 1 if not free_hand_2(hands["1"]) else 0

            #ex["HAND_IMBALANCE"] = 1 if (full_speaker_hand and not full_addressee_hand) else 0

            ## SPEAKER FULL HAND FEATURE
            # smart free hand feature
            '''
            # More fine-grained feature for card mentioned in strategy
            '''
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

            # if d["SPEAKER"] == "P1":
            #     # Indicator function that addressee edit smaller than speaker
            #     # if p2_ed < p1_ed:
            #     #     ex["ADDRESSEE_EDIT"] = 1.
            #     if c_all[0]:
            #         ex["A_SHOULD_ACT"] = 1.
            # else:
            #     # if p1_ed < p2_ed:
            #     #     ex["ADDRESSEE_EDIT"] = 1.
            #     if c_all[1]:
            #         ex["A_SHOULD_ACT"] = 1.
            ex["EDIT"] = ed
            label = d["POINTER"]

            x_text.append(d["DIALOGUE"])
            x.append(ex)
            y.append(label)

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
        self.count_vectorizer = CountVectorizer(ngram_range=(1,2))

        # Feature vectors converted to matrix  (num_samples, num_features)
        #feature_vec_transform = self.feature_vectorizer.fit_transform(x)
        count_vec_transform = self.count_vectorizer.fit_transform(x_text)

        self.classifier.fit(count_vec_transform, np.array(y))
        #self.classifier.fit(feature_vec_transform, np.array(y))


    def predict(self, x, x_text):
        """
        Provide features for a given group as a dict
        :param x: Data instance
        :param x_test: Test of data instance
        :return:
        """
        # Transform features to appropriate format
        #features_transformed = self.feature_vectorizer.transform(x)
        count_vec_transformed = self.count_vectorizer.transform(x_text)

        y_scores = None
        #y_scores = self.classifier.predict_proba(features_transformed)
        #y_scores = [y[1] for y in y_scores]

        # Scores using unigram features
        y_scores_uni = None
        y_scores_uni = self.classifier.predict_proba(count_vec_transformed)
        y_scores_uni = [y[1] for y in y_scores_uni]

        return self.classifier.predict(count_vec_transformed), y_scores, y_scores_uni


    def evaluate(self, test_data):
        """
        Test model
        :param test_data:
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
