#!/usr/bin/env python
#-*-encoding utf-8-*-
import base64
import zlib
import itertools
import re
import sys
#from bs4 import BeautifulSoup
from sys import stdin
import HTMLParser

from zipimport import zipimporter
zp = zipimporter("third_party.zip")
bs4 = zp.load_module("bs4")
BeautifulSoup = bs4.BeautifulSoup


class HTMLTextExtractor:
    def __init__(self):
        pass

    def extract(self, markup):
        soup = BeautifulSoup(markup, 'html.parser')

        for el in soup.find_all(['script', 'style', 'noindex']):
            el.decompose()

        return soup.get_text()


class WordsNormalizator:
    def __init__(self, text):
        wrds = re.split(r"[{}\[\]\(\),!\?\n\s\t\"\u200b:\.]", text)
        self.words = [wrd for wrd in wrds if WordsNormalizator.is_word(wrd)]

    @staticmethod
    def is_word(st):
        st = st.strip(",.:'\n\t \"-")
        return st != "" and not st.isdigit()

    @staticmethod
    def normalize_word(word):
        return word.lower().strip(",.:'\n\t \"-")

    def __iter__(self):
        return itertools.imap(WordsNormalizator.normalize_word, self.words)


def main():
    extractor = HTMLTextExtractor()
    for row in stdin:
        key, val = row.split("\t")
        html = zlib.decompress(base64.b64decode(val)).decode("utf8")
        normalizator = tuple()
        try:
            normalizator = WordsNormalizator(extractor.extract(html))
        except HTMLParser.HTMLParseError:
            pass

        for wrd in normalizator:
            print "%s\t%s" % (wrd.encode("unicode-escape"), key)

if __name__ == "__main__":
    main()
