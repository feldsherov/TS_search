#!/usr/bin/env python
import sys
import pickle
import os
from optparse import OptionParser

from bs4 import BeautifulSoup
import numpy as np
from sklearn.tree import DecisionTreeClassifier

__author__ = 'feldsherov'


class SentenceSplitter:
    def __init__(self):
        self.estimator = None

    @staticmethod
    def parse_data(path_to_data):
        xml_data = open(path_to_data, "r").read()
        xml_parser = BeautifulSoup(xml_data, "lxml")
        positions, sentences = list(), list()
        c_pos = 0
        paragraphs = list()
        for paragraph in xml_parser.find_all("paragraph"):
            paragraph_sentences = list()
            for el in paragraph.find_all("source"):
                txt = el.get_text()
                paragraph_sentences.append(txt)
                positions.append(c_pos + len(txt))
                sentences.append(txt)
                c_pos += len(txt) + 1
            paragraphs.append(" ".join(paragraph_sentences))

        text = "\n".join(paragraphs)
        text += chr(0)
        return text, positions

    @staticmethod
    def calc_features(text):
        features = list()
        for pos in range(len(text)):
            row = np.zeros(5)
            for sh in range(-2, 3):
                if 0 <= pos + sh < len(text):
                    row[sh] = ord(text[pos + sh])
            features.append(row)
        features = np.array(features)

        return features

    def fit(self, path):
        text, positions = SentenceSplitter.parse_data(path)

        features = SentenceSplitter.calc_features(text)
        target = np.zeros(features.shape[0])
        target[np.array(positions)] = 1

        self.estimator = DecisionTreeClassifier()
        self.estimator.fit(features, target)

    def predict(self, text):
        text += chr(0)

        features = SentenceSplitter.calc_features(text)
        prediction = self.estimator.predict(features)

        ans = list(np.where(prediction == 1)[0])
        ans.insert(0, 0)
        ans.append(-1)
        sentences = [text[ans[i - 1]: ans[i]] for i in range(1, len(ans))]
        return sentences

    def __call__(self, text):
        return self.predict(text)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--data",
                      action="store",
                      type="string",
                      dest="data_path",
                      default="./sentences.xml",
                      help="read train data from file")
    parser.add_option("-s", "--splitter",
                      action="store",
                      type="string",
                      dest="splitter_path",
                      default="./SentenceSplitter.pkl",
                      help="path for save splitter object")
    parser.add_option("-b", "--build",
                      action="store_true",
                      dest="only_build",
                      default=False,
                      help="only relearn splitter model without demonstration")

    options, args = parser.parse_args()

    if options.only_build and os.path.exists(options.splitter_path):
        print "Delete splitter model by path %s" % options.splitter_path
        os.remove(options.splitter_path)

    if os.path.isfile(options.splitter_path):
        print "Read splitter model by path %s" % options.splitter_path
        with open(options.splitter_path, "r") as pfile:
            splitter = pickle.load(pfile)
    else:
        print "Create splitter model by path %s\nUse dataset by path %s" % (options.splitter_path, options.data_path)

        splitter = SentenceSplitter()
        splitter.fit(options.data_path)
        with open(options.splitter_path, "w") as pfile:
            pickle.dump(splitter, pfile)

    if not options.only_build:
        print "Type text for splitting:"
        text = sys.stdin.read()
        print "Result :", "\n".join(splitter(text))
