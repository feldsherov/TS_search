#!/usr/bin/env python
from __future__ import print_function

import base64

from sys import stdin, stderr
from itertools import groupby, imap
from operator import itemgetter

from zipimport import zipimporter
zp = zipimporter("utils.zip")
varbyte = zp.load_module("varbyte")



__author__ = 'feldsherov'


def read_mapper_output(file_):
    for line in file_:
        yield line.rstrip().split()


def main():
    data = read_mapper_output(stdin)
    for current_word, docs_pos in groupby(data, itemgetter(0)):
        if current_word != "!!!DOC_LEN":
            print(current_word, end="\t")

        groups_by_word = imap(lambda a: (a[1], a[2]), docs_pos)
        if current_word == "!!!DOC_LEN":
            for doc_id, doc_len in groups_by_word:
                print("!!!DOC_LEN", doc_id, doc_len)
        else:
            groupby_word_and_doc_id = groupby(groups_by_word, itemgetter(0))
            for current_doc, positions in groupby_word_and_doc_id:
                current_positions = imap(itemgetter(1), positions)
                print(int(current_doc), base64.b64encode(varbyte.encode(current_positions)), end="\t")
            print()

if __name__ == "__main__":
    main()