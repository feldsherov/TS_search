#!/usr/bin/env python
import search
import optparse

__author__ = 'feldsherov'


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
    optparser = optparse.OptionParser()
    optparser.add_option("-p", "--path", dest="markers_path",
                         help="read MARKERS by path", default="./markers.tsv")
    optparser.add_option("-i", "--index", dest="index_path",
                         help="read INDEX by path", default="./index")
    (options, args) = optparser.parse_args()

    markes_f = open(options.markers_path, "r")

    index_path = options.index_path
    reader = search.IndexReader(index_path)
    handler = search.QueryHandler(reader)

    mismatch = 0
    ps_mismatch = 0
    bool_pos = list()
    bm_pos = list()
    ps_pos = list()

    for step, row in enumerate(markes_f):
        print 'step: %d ' % step, row
        query, ans = map(lambda a: a.decode("utf-8"), row.strip().split("\t"))
        sp = filter(lambda a: a != "", query.split())
        query = "&".join(sp)
        query_results, words_seq = handler.get_records(query)

        query_results = list(query_results)
        bool_res = map(norm_url, reader.get_urls_by_ids(map(lambda a: a.doc_id, query_results)))
        ans = norm_url(ans)
        if ans not in bool_res:
            mismatch += 1
        else:
            query_results_bm25 = search.rank_results(query_results, reader.get_urls_cout(),
                                                     words_seq=words_seq, order_by="bm25")
            query_results_ps = search.rank_results(query_results, reader.get_urls_cout(),
                                                   words_seq=words_seq, order_by="ps", top=200)

            bm25_res = map(norm_url, reader.get_urls_by_ids(map(lambda a: a.doc_id, query_results_bm25)))
            ps_res = map(norm_url, reader.get_urls_by_ids(map(lambda a: a.doc_id, query_results_ps)))

            if ans not in ps_res:
                ps_mismatch += 1
            else:
                ps_pos.append(ps_res.index(ans))

            bm_pos.append(bm25_res.index(ans))
            bool_pos.append(bool_res.index(ans))
        print "-----------------------------\n",\
              "mismatch %d \n" % mismatch, \
              "bool_pos_mean %f \n" % (float(sum(bool_pos)) / max(len(bool_pos), 1)), \
              "bm_pos_mean %f \n" % (float(sum(bm_pos)) / max(len(bm_pos), 1)), \
              "ps_mismatch %d \n" % ps_mismatch, \
              "ps_pos_mean %f \n" % (float(sum(ps_pos)) / max(len(ps_pos), 1)), \
              "-----------------------------\n"


if __name__ == "__main__":
    main()