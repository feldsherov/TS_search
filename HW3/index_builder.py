#!/usr/bin/env python

import os
import sys
import pickle
import shelve
import re
import nltk
import pymorphy2
from optparse import OptionParser

from html_text_extractor import HTMLTextExtractor
from splitter import SentenceSplitter

__author__ = 'feldsherov'


class Sentence:
    def __init__(self, text, position, words_tokenizer=nltk.tokenize.word_tokenize, morphy=pymorphy2.MorphAnalyzer()):
        self.text = text
        self.words = [morphy.parse(word)[0].normal_form for word in words_tokenizer(text)]
        self.position = position

    def get_words_intersection(self, words):
        return len(set(self.words) & set(words))


class DirectIndexWriter:
    def __init__(self, index_path, splitter=lambda a: re.split("[.!?]", a)):
        self.index_shlv = shelve.open(index_path, "w")
        self.text_extractor = HTMLTextExtractor(skip_tags=("a", "style", "script", "noindex", "title"))
        self.splitter = splitter
        self.word_tokenizer = nltk.tokenize.word_tokenize
        self.morph = pymorphy2.MorphAnalyzer()

    def add_to_index(self, name, markup):
        text = self.text_extractor.extract(markup)
        sentences = [Sentence(sentence_text, pos) for pos, sentence_text in enumerate(self.splitter(text))]
        self.index_shlv[name] = sentences

    def __del__(self):
        self.index_shlv.close()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-i", "--index",
                      action="store",
                      type="string",
                      dest="index_path",
                      default="./index",
                      help="write index to FILE")
    parser.add_option("-s", "--splitter",
                      action="store",
                      type="string",
                      dest="splitter_path",
                      default="./SentenceSplitter.pkl",
                      help="path for reading splitter object")
    parser.add_option("-u", "--urls",
                      action="store",
                      type="string",
                      dest="urls_path",
                      default="./urls",
                      help="directory with html files")
    options, args = parser.parse_args()

    if not os.path.isdir(options.urls_path):
        raise ValueError("path to urls must be directory")

    if os.path.isfile(options.splitter_path):
        with open(options.splitter_path, "r") as pfile:
            splitter = pickle.load(pfile)
        index_writer = DirectIndexWriter(options.index_path, splitter=splitter)
    else:
        print >>sys.stderr, "Sentence splitter not found, using trivial regexp."
        index_writer = DirectIndexWriter(options.index_path)

    print "Read splitter model from %s" % options.splitter_path
    print "Creating direct index for files in directory %s" % options.urls_path
    print "Writing index to path %s" % options.index_path

    for pt in os.listdir(options.urls_path):
        with open(os.path.join(options.urls_path, pt), "r") as inp:
            index_writer.add_to_index(pt, inp.read())