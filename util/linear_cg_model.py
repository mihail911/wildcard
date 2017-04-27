import numpy as np

from collections import Counter
from model_util import free_hand, compute_ed
from parse_annotations import parse_all
from scipy import stats
from sklearn import linear_model
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import f_regression
from sklearn.linear_model import LinearRegression

"""
Model common ground influence using linear regression
"""

class CustomLinearRegression(linear_model.LinearRegression):
    """
    LinearRegression class after sklearn's,
    This class sets the intercept to 0 by default, since usually we include it
    in X.
    """
    def __init__(self, *args, **kwargs):
        if not "fit_intercept" in kwargs:
            kwargs['fit_intercept'] = False
        super(CustomLinearRegression, self).__init__(*args, **kwargs)

    def fit(self, X, y, n_jobs=1):
        self = super(CustomLinearRegression, self).fit(X, y, n_jobs)

        return self


class LinearCGModel(object):
    """
    Linear regression applied to common ground features
    """
    def __init__(self):
        self.classifier = CustomLinearRegression()


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

            # Mentioned strategy
            if len(d["P1_NEED"]) > 0 or len(d["P2_NEED"]) > 0:
                ex["MENTIONED_STRATEGY"] = 1.

            if d["SPEAKER"] == "P1":
                # Indicator function that addressee edit smaller than speaker
                if p2_ed < p1_ed:
                    ex["ADDRESSEE_EDIT"] = 1.
                # TODO: Whether to include negative feature?
            else:
                if p1_ed < p2_ed:
                    ex["ADDRESSEE_EDIT"] = 1.


            #ex["EDIT"] = ed
            label = d["POINTER"]

            x.append(ex)
            y.append(label)

        return x, y


    def train(self, data):
        """
        Train model
        :param data:
        :return:
        """
        x, y = self._featurize(data)
        self.feature_vectorizer = DictVectorizer()

        # Feature vectors converted to matrix  (num_samples, num_features)
        feature_vec_transform = self.feature_vectorizer.fit_transform(x)
        arr = feature_vec_transform.toarray()
        self.classifier.fit(feature_vec_transform, np.array(y))
        f, p = f_regression(feature_vec_transform, np.array(y), center=False)
        print "F: ", f
        print "P: ", p



if __name__ == "__main__":
    annotation_dir = "../data/annotated"
    utterances = parse_all(annotation_dir)
    model = LinearCGModel()
    model.train(utterances)