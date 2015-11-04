#!/usr/bin/env python
import sys
import os
import shelve
import base64
import struct

__author__ = 'feldsherov'


def add_to_index(ind, shlv, fl):
    for row in fl:
        wrd, ids = row.split("\t")
        wrd, ids = wrd, base64.b64decode(ids)
        shlv[wrd] = ind.tell()
        ind.write(struct.pack("l", len(ids)))
        ind.write(ids)


def main():
    src_dir = sys.argv[1]
    index_path = sys.argv[2]
    urls_path = sys.argv[3]
    ind = open(index_path, "wb")
    shlv = shelve.open(index_path + "_shlv")
    shlv_urls = shelve.open(index_path + "_urls")
    for file_path in os.listdir(src_dir):
        file_path = os.path.abspath(src_dir + file_path)
        if os.path.isfile(file_path):
            add_to_index(ind, shlv, open(file_path, "r"))
    ind.close()
    shlv.close()

    cp = 0
    for row in open(urls_path, "r"):
        cp += 1
        k, url = row.strip().split("\t")
        shlv_urls[struct.pack("l", int(k))] = url
    shlv_urls["count"] = cp
    shlv_urls.close()


if __name__ == "__main__":
    main()