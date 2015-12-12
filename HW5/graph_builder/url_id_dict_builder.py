#!/usr/bin/env python
import pickle
import sys

def norm_url(url):
    if "?" in url:
        sp = url.split("?")
        url = "".join(sp[:-1])
    if url.endswith("/"):
        url = url[:-1]
    if ".ru" in url:
        url = url.split(".ru")[-1]
    return url


if __name__ == "__main__":
    urls_file = open("urls.txt", "r")
    url_id_dict = dict()
    for row in urls_file:
        url_id, url = row.split()
        url_id = int(url_id)
        if url_id % 1000 == 0:
            print "Current url_id %s" % url_id
        url = norm_url(url)
        if url in url_id_dict:
            print >>sys.stderr, "Collision: %s" % url
        url_id_dict[url] = url_id
    urls_file.close()

    dict_file = open("url_id_dict.pkl", "w")
    pickle.dump(url_id_dict, dict_file)
    dict_file.close()
