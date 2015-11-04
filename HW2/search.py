#!/usr/bin/env python
import os
import sys
import struct
import shelve
import heapq
import operator
import itertools

from varbyte import VarByte

__author__ = 'feldsherov'


class IndexReader:
    def __init__(self, index_path):
        self.ind = open(index_path, "rb")
        self.shlv_urls = shelve.open(index_path + "_urls")
        self.shlv_offsets = shelve.open(index_path + "_shlv")

    def get_record(self, wrd):
        if wrd not in self.shlv_offsets.keys():
            return iter(list())
        offset = self.shlv_offsets[wrd]
        self.ind.seek(offset)
        vb_len = struct.unpack("l", self.ind.read(struct.calcsize("l")))[0]
        vb_code = self.ind.read(vb_len)
        return iter(VarByte.decode(vb_code))

    def get_urls_by_ids(self, ids):
        result = list()
        for id_ in ids:
            try:
                result.append(self.shlv_urls[struct.pack("l", id_)])
            except KeyError:
                print >>sys.stderr, id_
        return iter(result)

    def get_urls_cout(self):
        return self.shlv_urls["count"]


class QueryHandler:
    def __init__(self, index_reader):
        self.reader = index_reader
        self.count_urls = index_reader.get_urls_cout()

    def get_docs(self, query):
        for el in ("(", ")", "!", "&", "|"):
            query = query.replace(el, " %s " % el)

        terms = ["("] + filter(lambda a: a != "", query.split()) + [")"]
        operations = "|&!"
        brackets = "()"
        priority_dict = {"(": -1, "|": 0, "&": 1, "!": 2}
        operations_dict = {"|": QueryHandler._or, "&": QueryHandler._and, "!": QueryHandler._not}
        operations_st = list()
        iters_st = list()
        for t in terms:
            if t in operations:
                while priority_dict[operations_st[-1]] > priority_dict[t]:
                    ps = operations_st[-1]
                    operations_st.pop()
                    if ps != "!":
                        it1 = iters_st[-1]
                        it2 = iters_st[-2]
                        iters_st.pop()
                        iters_st.pop()
                        opr = operations_dict[ps]
                        iters_st.append(iter(opr(it1, it2)))
                    else:
                        opr = operations_dict[ps]
                        iters_st[-1] = iter(opr(self.count_urls - 1, iters_st[-1]))
                operations_st.append(t)
            elif t in brackets:
                if t == "(":
                    operations_st.append(t)
                else:
                    while operations_st[-1] != "(":
                        ps = operations_st[-1]
                        operations_st.pop()
                        if ps != "!":
                            it1 = iters_st[-1]
                            it2 = iters_st[-2]
                            iters_st.pop()
                            iters_st.pop()
                            opr = operations_dict[ps]
                            iters_st.append(iter(opr(it1, it2)))
                        else:
                            opr = operations_dict[ps]
                            iters_st[-1] = iter(opr(self.count_urls - 1, iters_st[-1]))
                    operations_st.pop()
            else:
                iters_st.append(self.reader.get_record(t))

        while len(iters_st) > 1:
            ps = operations_st[-1]
            operations_st.pop()
            if ps != "!":
                it1 = iters_st[-1]
                it2 = iters_st[-2]
                iters_st.pop()
                iters_st.pop()
                opr = operations_dict[ps]
                iters_st.append(iter(opr(it1, it2)))
            else:
                opr = operations_dict[ps]
                iters_st[-1] = iter(opr(self.count_urls - 1, iters_st[-1]))
        return iters_st[-1]


    @staticmethod
    def _or(self, iter1, iter2):
        return itertools.imap(operator.itemgetter(0),
                              itertools.groupby(heapq.merge(iter1, iter2))
        )

    @staticmethod
    def _or(iter1, iter2):
        return itertools.imap(operator.itemgetter(0),
                              itertools.groupby(heapq.merge(iter1, iter2)))

    @staticmethod
    def _not(urls_max_id, iter):
        urls_max_id += 1
        cp = 0
        try:
            st = iter.next()
            while cp < urls_max_id:
                if cp != st:
                    yield cp
                    cp += 1
                else:
                    cp += 1
                    st = iter.next()
        except StopIteration:
            while cp < urls_max_id:
                yield cp
                cp += 1

    @staticmethod
    def _and(iter1, iter2):
        try:
            st1 = iter1.next()
            st2 = iter2.next()
            while True:
                if st1 == st2:
                    yield st1
                    st1 = iter1.next()
                    st2 = iter2.next()
                elif st1 > st2:
                    st2 = iter2.next()
                elif st1 < st2:
                    st1 = iter1.next()
                else:
                    raise IndexError("Invalid case in __and")
        except StopIteration:
            pass


def main():
    index_path = sys.argv[1]
    reader = IndexReader(index_path)
    handler = QueryHandler(reader)
    query = raw_input()
    ids = handler.get_docs(query)
    print "\n".join(reader.get_urls_by_ids(ids))


if __name__ == "__main__":
    main()