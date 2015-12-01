#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import base64
import zlib
import itertools
import re
import string
from sys import stdin, stderr
import HTMLParser

import pymorphy2

#importing with zipimport
from zipimport import zipimporter

zp = zipimporter("utils.zip")
bs4 = zp.load_module("bs4")
BeautifulSoup = bs4.BeautifulSoup
HTMLTextExtractor_module = zp.load_module("html_text_extractor")
HTMLTextExtractor = HTMLTextExtractor_module.HTMLTextExtractor


class WordsNormalizer:
    def __init__(self, text):
        self.morph = pymorphy2.MorphAnalyzer()
        self.letters_set = set(unicode(string.letters) +
                               u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
        self.digits_set = set(unicode(string.digits))

        words = re.split(r"[{}\[\]\(\),!\?\n\s\t\"\u200b:\.]", text)
        self.words = [word for word in words if self.is_word(word)]

    def is_word(self, st):
        st = st.strip(",.:'\n\t \"-")
        st_set = set(st)
        f_has_digit = len(self.digits_set & st_set) > 0
        f_has_letter = len(self.letters_set & st_set) > 0
        return f_has_digit or f_has_letter

    def normalize_word(self, word):
        word = word.lower().strip(",.:'\n\t \"-")
        return self.morph.parse(word)[0].normal_form

    def __iter__(self):
        return itertools.imap(self.normalize_word, self.words)


def main():
    extractor = HTMLTextExtractor()
    for row in stdin:
        doc_id, val = row.split("\t")
        html = zlib.decompress(base64.b64decode(val)).decode("utf8")
        normalizer = tuple()
        try:
            normalizer = WordsNormalizer(extractor.extract(html))
        except HTMLParser.HTMLParseError:
            print("Can't parse file %s" % doc_id, file=stderr)

        pos_tmp = 0
        for pos, wrd in enumerate(normalizer):
            print("%s %06d %06d\t" % (wrd.encode("unicode-escape"), int(doc_id), pos))
            pos_tmp = pos

        print("!!!DOC_LEN %s %s\t" % (int(doc_id), pos_tmp))



if __name__ == "__main__":
    main()
