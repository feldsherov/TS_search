#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import stdin, stderr
import zlib
import base64

#importing with zipimport
from zipimport import zipimporter
import zipfile
import pickle
zp = zipimporter("utils.zip")
bs4 = zp.load_module("bs4")
BeautifulSoup = bs4.BeautifulSoup

def norm_url(url):
    if "?" in url:
        sp = url.split("?")
        url = "".join(sp[:-1])
    if url.endswith("/"):
        url = url[:-1]
    if ".ru" in url:
        url = url.split(".ru")[-1]
    return url


def main():
    dict_file = zipfile.ZipFile("url_id_dict.zip", "r")
    pkl_string = dict_file.read("url_id_dict.pkl")
    url_id_dict = pickle.loads(pkl_string)
    for row in stdin:
        doc_id, val = row.split("\t")
        doc_id = int(doc_id)
        html = zlib.decompress(base64.b64decode(val)).decode("utf8")
        normalizer = tuple()
        bs = BeautifulSoup(html, "lxml")
        for anchor in bs.find_all("a"):
            try:
                link = anchor['href']
            except KeyError:
                pass
            link = norm_url(link)
            if link in url_id_dict:
                link_id = url_id_dict[link]
                print "%s\t%s" % (doc_id, link_id)


if __name__ == "__main__":
    main()
