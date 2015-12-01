#!/usr/bin/env python
import sys
import os
import shelve
import base64
import struct
import varbyte

__author__ = 'feldsherov'


def add_to_index(ind, shlv, shlv_len, fl):
    for row in fl:
        if "!!!DOC_LEN" in row:
            doc_id, doc_len = row.rstrip().split()[1:]
            shlv_len[doc_id] = int(doc_len)
        else:
            lst = row.rstrip().split("\t")
            wrd, lst = lst[0], lst[1:]

            lst = [el.split(" ") for el in lst]
            shlv[wrd] = ind.tell()
            doc_ids, positions_by_docs = zip(*lst)
            ids = varbyte.encode(sorted(map(int, doc_ids)))
            ind.write(struct.pack("l", len(ids)))
            ind.write(ids)
            for bs64_positions in positions_by_docs:
                vb_positions = base64.b64decode(bs64_positions)
                ind.write(struct.pack("l", len(vb_positions)))
                ind.write(vb_positions)


def main():
    src_dir = sys.argv[1]
    index_path = sys.argv[2]
    urls_path = sys.argv[3]
    ind = open(index_path, "wb")
    shlv = shelve.open(index_path + "_shlv")
    shlv_urls = shelve.open(index_path + "_urls")
    shlv_len = shelve.open(index_path + "_len")
    for file_path in os.listdir(src_dir):
        file_path = os.path.abspath(src_dir + file_path)
        if os.path.isfile(file_path):
            add_to_index(ind, shlv, shlv_len, open(file_path, "r"))
    ind.close()
    shlv.close()
    shlv_len.close()

    cp = 0
    for row in open(urls_path, "r"):
        cp += 1
        k, url = row.strip().split("\t")
        shlv_urls[struct.pack("l", int(k))] = url
    shlv_urls["count"] = cp
    shlv_urls.close()


if __name__ == "__main__":
    main()