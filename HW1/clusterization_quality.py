#!/Users/feldsherov/anaconda/bin/python
__author__ = 'feldsherov'

import sys
import re
import numpy as np
import random

COUNT_STEPS = 10


def normalize_url(url):
    """
    :param url: url for normalizing
    :return: normalized url
    """
    url = url.strip()
    url = url.strip("/")
    if url.startswith(r"http://"):
        url = url[len(r"http://"):]

    url = url.split("/", 1)[1]
    return "/" + url


def get_clusters(urls, regexps):
    clusters = np.zeros(len(urls), dtype=int)
    count_of_clusters = len(regexps)
    for i, url in enumerate(urls):
        cnt = np.zeros(count_of_clusters, dtype=float)
        for clst in range(count_of_clusters):
            for r in regexps[clst]:
                if r.match(url):
                    cnt[clst] += 1

        cnt[clst] /= len(regexps[clst])

        clusters[i] = cnt.argmax()

    return clusters


def get_quality(actual_examined, actual_general, regexps):
    examined_clusters = get_clusters(actual_examined, regexps)
    general_clusters = get_clusters(actual_general, regexps)

    count_of_clusters = len(regexps)

    g_bc = np.bincount(general_clusters, minlength=count_of_clusters)
    e_bc = np.bincount(examined_clusters, minlength=count_of_clusters)

    sm = g_bc + e_bc
    mx = np.maximum(g_bc, e_bc)
    nz = np.nonzero(sm)
    
    result = mx[nz].astype(dtype=float).sum() / sm[nz].sum()
    
    return result
    #return results.mean()


if __name__ == "__main__":
    urls_general_path = sys.argv[1]
    urls_examined_path = sys.argv[2]
    regs_path = sys.argv[3]

    general_all = [normalize_url(url) for url in open(urls_general_path, "r").readlines()]
    examined_all = [normalize_url(url) for url in open(urls_examined_path, "r").readlines()]

    fin = open(regs_path, "r")
    regs_s = [row.split() for row in fin.readlines()]
    fin.close()

    regexps = list()
    for rw in regs_s:
        regexps.append([re.compile(s) for s in rw])

    count_of_clusters = len(regs_s)

    results = list()
    examined_size = len(examined_all)
    for i in range(COUNT_STEPS):
        actual_general = random.sample(general_all, examined_size / 4)
        actual_examined = random.sample(examined_all, examined_size / 4)

        results.append(get_quality(actual_examined, actual_general, regexps))

    print "Results:", results

    print "Final quality: %f" % (float(sum(results)) / len(results))
