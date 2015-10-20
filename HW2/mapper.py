#-*-encoding utf-8-*-
import base64
import zlib
import itertools
import re
import sys
from bs4 import BeautifulSoup
from sys import stdin


class HTMLTextExtractor:
    def __init__(self):
        pass

    def extract(self, markup):
        soup = BeautifulSoup(markup, "lxml")

        for el in soup.body.find_all(['script', 'style', 'noindex']):
            el.decompose()

        return soup.get_text()


class WordsNormalizator:
    def __init__(self, text):
        wrds = re.split(r"[{}\[\]\(\),!\?\n\s\t\"\u200b:\.]", text, flags=re.UNICODE)
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
        normalizator = WordsNormalizator(extractor.extract(html))
        for wrd in normalizator:
            print "%s\t%s" % (wrd.encode("unicode-escape"), key)

if __name__ == "__main__":
    main()
