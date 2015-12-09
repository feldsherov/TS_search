#!/usr/bin/env python
import sys
import struct
import shelve
import operator
import itertools
import pymorphy2
import optparse
import math
import os

import varbyte

__author__ = 'feldsherov'


class QTree:
    def __init__(self, word=None, left=None, right=None, operation=None):
        self.word = word
        self.left = left
        self.right = right
        self.operation = operation

    def __or__(self, other):
        return QTree(left=self, right=other, operation="|")

    def __and__(self, other):
        return QTree(left=self, right=other, operation="&")

    def __invert__(self):
        return QTree(left=self, operation="!")


class IndexRecord:
    def __init__(self, word, doc_id, positions, df, doc_len):
        self.word = word
        self.doc_id = doc_id
        self.positions = positions
        self.df = df
        self.tf = len(positions)
        self.doc_len = doc_len

    def __cmp__(self, other):
        return cmp(self.doc_id, other.doc_id)


class QueryResult:
    def __init__(self, record=None):
        self.doc_id = None
        self.records = list()

        if record is not None:
            self.doc_id = record.doc_id
            self.records.append(record)

    def add_record(self, record):
        if self.doc_id is None:
            self.doc_id = record.doc_id

        if self.doc_id != record.doc_id:
            raise ValueError("In query result all records must have the same document id")

        self.records.append(record)

        return self

    def join(self, q_result):
        if self.doc_id is not None and q_result.doc_id is not None and self.doc_id != q_result.doc_id:
            raise ValueError("In query result all records must have the same document id")

        self.records.extend(q_result.records)

        return self

    def __cmp__(self, other):
        return cmp(self.doc_id, other.doc_id)

    def __iter__(self):
        return iter(self.records)


class IndexReader:
    def __init__(self, index_path):
        self.ind = open(index_path, "rb")
        self.shlv_urls = shelve.open(index_path + "_urls")
        self.shlv_offsets = shelve.open(index_path + "_shlv")
        self.shlv_len = shelve.open(index_path + "_len")

    def get_record(self, wrd):
        if wrd not in self.shlv_offsets.keys():
            return iter(list())
        offset = self.shlv_offsets[wrd]
        self.ind.seek(offset)
        vb_len = struct.unpack("l", self.ind.read(struct.calcsize("l")))[0]
        vb_code = self.ind.read(vb_len)
        doc_ids = varbyte.decode(vb_code)
        positions = list()
        for _ in doc_ids:
            vb_len = struct.unpack("l", self.ind.read(struct.calcsize("l")))[0]
            vb_code = self.ind.read(vb_len)
            positions.append(varbyte.decode(vb_code))

        df = len(doc_ids)

        return iter([QueryResult(IndexRecord(word=wrd,
                                             doc_id=c_id,
                                             positions=positions,
                                             df=df,
                                             doc_len=self.shlv_len[str(c_id)]
                                             ))
                     for c_id, positions in zip(doc_ids, positions)])

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
        self.morph = pymorphy2.MorphAnalyzer()

    def parse_query(self, query):
        for el in ("(", ")", "!", "&", "|"):
            query = query.replace(el, " %s " % el)

        words_seq = list()

        terms = ["("] + filter(lambda a: a != "", query.split()) + [")"]
        operations = "|&!"
        brackets = "()"
        priority_dict = {"(": -1, "|": 0, "&": 1, "!": 2}
        operations_dict = {"|": operator.or_, "&": operator.and_, "!": operator.invert}
        operations_st = list()
        query_st = list()
        for t in terms:
            if t in operations:
                while priority_dict[operations_st[-1]] > priority_dict[t]:
                    ps = operations_st[-1]
                    operations_st.pop()
                    if ps != "!":
                        q1 = query_st[-1]
                        q2 = query_st[-2]
                        query_st.pop()
                        query_st.pop()
                        opr = operations_dict[ps]
                        query_st.append(opr(q1, q2))
                    else:
                        opr = operations_dict[ps]
                        query_st[-1] = opr(query_st[-1])
                operations_st.append(t)
            elif t in brackets:
                if t == "(":
                    operations_st.append(t)
                else:
                    while operations_st[-1] != "(":
                        ps = operations_st[-1]
                        operations_st.pop()
                        if ps != "!":
                            q1 = query_st[-1]
                            q2 = query_st[-2]
                            query_st.pop()
                            query_st.pop()
                            opr = operations_dict[ps]
                            query_st.append(opr(q1, q2))
                        else:
                            opr = operations_dict[ps]
                            query_st[-1] = opr(query_st[-1])
                    operations_st.pop()
            else:
                t = self.morph.parse(t)[0].normal_form
                query_st.append(QTree(word=t))
                words_seq.append(t)

        while len(query_st) > 1:
            ps = operations_st[-1]
            operations_st.pop()
            if ps != "!":
                q1 = query_st[-1]
                q2 = query_st[-2]
                query_st.pop()
                query_st.pop()
                opr = operations_dict[ps]
                query_st.append(opr(q1, q2))
            else:
                opr = operations_dict[ps]
                query_st[-1] = opr(query_st[-1])
        return (query_st[-1], words_seq) if query_st else (QTree(word=""), list())

    def execute_query(self, qtree):
        operations_dict = {"|": QueryHandler.or_, "&": QueryHandler.and_, "!": QueryHandler.not_}

        left_res, right_res = iter(tuple()), iter(tuple())
        if qtree.left is not None:
            left_res = self.execute_query(qtree.left)
        if qtree.right is not None:
            right_res = self.execute_query(qtree.right)

        if qtree.word is not None:
            result_list = self.reader.get_record(qtree.word.encode("unicode-escape"))
            return iter(result_list)
        else:
            opr = operations_dict[qtree.operation]
            return iter(opr(left_res, right_res))

    def get_records(self, query):
        qtree, words_seq = self.parse_query(query)
        return self.execute_query(qtree), words_seq

    @staticmethod
    def or_(iter1, iter2):
        try:
            st1 = iter1.next()
            st2 = iter2.next()
            while True:
                if st1 == st2:
                    yield st1.join(st2)
                    st1 = iter1.next()
                    st2 = iter2.next()
                elif st1 > st2:
                    yield st2
                    st2 = iter2.next()
                elif st1 < st2:
                    yield st1
                    st1 = iter1.next()
                else:
                    raise IndexError("Invalid case in __or")
        except StopIteration:
            pass

    @staticmethod
    def not_(urls_max_id, iter):
        urls_max_id += 1
        cp = 0
        try:
            st = iter.next()
            while cp < urls_max_id:
                if cp != st:
                    yield IndexRecord(doc_id=cp)
                    cp += 1
                else:
                    cp += 1
                    st = iter.next()
        except StopIteration:
            while cp < urls_max_id:
                yield IndexRecord(doc_id=cp)
                cp += 1

    @staticmethod
    def and_(iter1, iter2):
        try:
            st1 = iter1.next()
            st2 = iter2.next()
            while True:
                if st1 == st2:
                    yield st1.join(st2)
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


def calc_bm25(q_result, cnt_docs):
    k1, b = 2, 0.75
    eps = 1e-3
    ans = 0
    for record in q_result.records:
        idf = math.log10(cnt_docs / float(record.df))
        ans += record.tf * idf / (record.tf + k1 * (b + record.doc_len * (1 - b)))
    return ans


def count_inversion(sequence):
    """
        Count inversions in a sequence of numbers
    """
    return sum([1
                for i in range(len(sequence) - 1, -1, -1)
                for j in range(i - 1, -1, -1)
                if sequence[i] < sequence[j]])


def calc_one_passage_rank(passage):
    if not filter(None, passage):
        return -1

    min_el = min(filter(None, passage))
    max_el = max(filter(None, passage))
    max_count = max(len(passage) * (len(passage) - 1), 1)
    inv_rank = (max_count - count_inversion(passage)) / max_count
    abs_dist_rank = 0.999 ** min_el
    relative_dist_rank = 0.8 ** (max_el - min_el - len(passage) + 1)
    return inv_rank + abs_dist_rank + relative_dist_rank


def calc_passage_rank(q_result, words_seq):
    """
    :param q_result:
    :param words_seq: list -- sequence of words in query
    :return:
    """

    words_seq = [el.encode("unicode-escape") for el in words_seq]

    all_positions = list()
    for record in q_result.records:
        all_positions.extend(zip(record.positions, itertools.repeat(record.word)))

    all_positions.sort(key=lambda a: a[0])

    passage = [None] * len(words_seq)
    ans = 0

    for el in all_positions:
        if el[1] not in words_seq:
            raise ValueError("word %s not in query" % el)

        passage[words_seq.index(el[1])] = el[0]

        ans = max(ans, calc_one_passage_rank(passage))

    return ans


def rank_results(query_results, cnt_docs, words_seq, order_by="bm25", top=100):
    query_results = list(query_results)
    bm25_order = None

    if order_by in ("bm25", "ps"):
        query_results.sort(key=lambda a: -calc_bm25(a, cnt_docs))
        bm25_order = query_results

    if order_by == "bm25":
        return bm25_order
    elif order_by == "ps":
        passage_order = bm25_order[:top]
        passage_order.sort(key=lambda a: -calc_passage_rank(a, words_seq))
        return passage_order

    return query_results


def main():
    optparser = optparse.OptionParser()
    optparser.add_option("-i", "--index", dest="index_path",
                         help="read INDEX by path", default="./index")

    optparser.add_option("-m", "--mode", dest="mode",
                         help="mode \n b for binary \n bm25 for ranked by bm25 \n ps for passage algorithm", default="b")

    optparser.add_option("-o", "--operations", dest="operations",
                         action="store_true",
                         help="include binary logic operations")

    (options, args) = optparser.parse_args()

    index_path = options.index_path
    reader = IndexReader(index_path)
    handler = QueryHandler(reader)

    if options.mode not in ("b", "bm25", "ps"):
        optparser.error("Mode option must be ps, bm25 or b")

    for row in sys.stdin:
        query = row.decode("utf-8")

        if not options.operations:
            sp = filter(lambda a: a != "", query.split())
            query = "|".join(sp)

        query_results, words_seq = handler.get_records(query)
        query_results = list(query_results)
        if options.mode == "b":
            print "\n".join(reader.get_urls_by_ids(map(lambda a: a.doc_id, query_results)))
        else:
            query_results = rank_results(query_results, reader.get_urls_cout(), words_seq=words_seq, order_by=options.mode)
            print "\n".join(reader.get_urls_by_ids(map(lambda a: a.doc_id, query_results)))


if __name__ == "__main__":
    main()