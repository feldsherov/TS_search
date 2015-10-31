#!/Users/feldsherov/anaconda/bin/python
__author__ = 'feldsherov'

import sys
import re
import random

import numpy as np
from sklearn.cluster import KMeans as kmeans

COUNT_OF_CLUSTERS = 3


class Clusterizator_kmeans:
    """
    Implement clustering algorithm according
    """

    def __init__(self, **kwargs):
        self.k = kwargs['k']
        self.max_steps = kwargs.get('max_steps', 200)
        assert(self.max_steps > 1)
        assert(self.k >= 1)
        return

    def fit(self, x, y=None):
        self.x_len = len(x)
        self.features_len = len(x[0])

        centroids = np.array([x[i] for i in np.random.choice(self.x_len, self.k, replace=False)])
        old_clasters = None

        for step in range(self.max_steps):
            clasters = np.zeros(self.x_len)
            for el in xrange(self.x_len):
                pos = min(map(lambda ell: (np.sum((x[el] - ell[1])**2), ell[0]), enumerate(centroids)))
                clasters[el] = pos[1]

            if old_clasters is not None and np.array_equal(clasters, old_clasters):
                break

            centroids = np.zeros(self.k*self.features_len).reshape((self.k, self.features_len))
            cnts = np.zeros(self.k)

            for i, clst in enumerate(clasters):
                centroids[clst] += x[i]
                cnts[clst] += 1

            for i in range(self.k):
                if cnts[i] != 0:
                    centroids[i] /= cnts[i]

            old_clasters = clasters

        self.last_steps = step
        self.centroids = centroids
        return self

    def predict(self, x):
        """
        Using computed model parameters predict cluster
        for all objects from x
        """
        return [min(map(lambda ell: (np.sum((x[el] - ell[1])**2), ell[0]), enumerate(self.centroids)))[1]
                for el in xrange(self.x_len)]

    def fit_predict(self, x, y=None):
        self.fit(x, y)
        return self.predict(x)

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


def generate_regexps_by_url(url):
    segments = url.split(r"/")[1:]
    count_of_segments = "^" + "(/[^\/]+){" + str(len(segments)) + "}" + "/?$"

    segments_match = list()
    for i, s in enumerate(segments):
        segments_match.append("^" + "(/[^\/]+){" + str(i) + "}" + "/" + s +
                              "(/[^\/]+){" + str(len(segments) - 1 - i) + "}" + "/?$")

        if s.isdigit():
            segments_match.append("^" + "(/[^\/]+){" + str(i) + "}" + "/[0-9]+" +
                                  "(/[^\/]+){" + str((len(segments) - 1 - i)) + "}" + "/?$")

    check_extention = None
    ext = url.split(".")[-1]

    if "/" not in ext:
        check_extention = "^.+\." + ext + "$"

    regexps = [count_of_segments] + segments_match

    if check_extention is not None:
        regexps.append(check_extention)

    return regexps


def normilize_all(urls):
    return [normalize_url(url) for url in urls]

def generate_regexps_all(urls):
    regexps_all = list()
    for url in urls:
        regexps_all += generate_regexps_by_url(url)

    return regexps_all


def select_regexps(urls, regexps, alfa=0.1):
    regexps_s = regexps
    regexps = [re.compile(s) for s in regexps_s]

    counts = [0 for i in range(len(regexps))]

    for i, r in enumerate(regexps):
        for url in urls:
            if r.match(url):
                counts[i] += 1

    order = [i for i in range(len(counts)) if counts[i] > len(urls) * alfa]

    return [(regexps[el], regexps_s[el]) for el in order]


def create_features(regexps, urls):
    features = np.zeros(len(regexps) * len(urls)).reshape(len(urls), len(regexps))

    for i, url in enumerate(urls):
        for j, r in enumerate(regexps):
            if r[0].match(url):
                features[i][j] = 1

    return features


def generate_regexp_for_clusters(regexps, features, clusters):
    cnt = np.zeros(COUNT_OF_CLUSTERS * features.shape[1], dtype=float).reshape(COUNT_OF_CLUSTERS, features.shape[1])
    for f_id in range(features.shape[1]):
        for url_id in range(features.shape[0]):
            cnt[clusters[url_id]][f_id] += features[url_id][f_id]

    for f_id in range(cnt.shape[1]):
        cs = 0
        for c_id in range(COUNT_OF_CLUSTERS):
            cs += cnt[c_id][f_id]

        for c_id in range(COUNT_OF_CLUSTERS):
            cnt[c_id][f_id] /= cs

    ans = [list() for el in range(COUNT_OF_CLUSTERS)]

    for f_id in range(features.shape[1]):
        for c_id in range(COUNT_OF_CLUSTERS):
            if cnt[c_id][f_id] > 0.7:
                ans[c_id].append(regexps[f_id][1])

    return ans

if __name__ == "__main__":
    np.random.seed(179)
    urls_general_path = sys.argv[1]
    urls_examined_path = sys.argv[2]

    urls_examined = normilize_all(open(urls_examined_path, "r").readlines()[:1000])
    urls_general = normilize_all(random.sample(open(urls_general_path, "r").readlines(), len(urls_examined)))

    urls_all = urls_examined + urls_general

    regexps = list(set(generate_regexps_all(urls_all)))

    actual_regexps = select_regexps(urls_all, regexps)

    features = create_features(actual_regexps, urls_all)
    kmeans_obj = Clusterizator_kmeans(k=COUNT_OF_CLUSTERS)

    clusters = kmeans_obj.fit_predict(features)

    fout = open("clusterization.txt", "w")
    for i, url in enumerate(urls_all):
        print >>fout, url, clusters[i]
    fout.close()

    fout = open("som/urls.vec", "w")
    print >>fout, "$XDIM %d" % features.shape[0]
    print >>fout, "$YDIM 1"
    print >>fout, "$VEC_DIM %d" % features.shape[1]

    for i, url in enumerate(urls_all):
        print >>fout, " ".join(map(str, features[i])), url
    fout.close()

    fout = open("som/urls.tv", "w")
    print >>fout, "$TYPE template"
    print >>fout, "$XDIM 2"
    print >>fout, "$YDIM %d" % features.shape[0]
    print >>fout, "$VEC_DIM %d" % features.shape[1]
    for url, reg in enumerate(actual_regexps):
        print >>fout, url, reg[1]
    fout.close()

    fout = open("som/urls.cls", "w")
    for url_ex in urls_examined:
        print >>fout, "%s\tcls_1" % url_ex
    for url_g in urls_general:
        print >>fout, "%s\tcls_0" % url_g

    fout.close()


    clst_desc = generate_regexp_for_clusters(actual_regexps, features, clusters)
    fout = open("clusters_desc.txt", "w")
    for l in clst_desc:
        if len(l) > 0:
            print >>fout, " ".join(l)
    fout.close()
