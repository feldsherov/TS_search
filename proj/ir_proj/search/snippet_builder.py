#!coding: utf-8
import pymorphy2
import numpy as np
import re

__author__ = 'danpol'


###########################################################################
#                                                                         #
#    SnippetBuilder().build_snippet(doc, u'дикорастущие каштаны', 300)    #
#                                                                         #
###########################################################################


class SnippetBuilder:
    TDOT = u"...".encode("utf-8")
    SPEC = u'?!@#$%^&*()_+=-–\'"\\,./|}{][`~:;–<>«» '.encode("utf-8")

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        self.norm = lambda x: self.morph.parse(x)[0].normal_form

    def normalize(self, query):
        return map(self.norm, query.split(" "))

    def build_snippet(self, document, query, length):
        '''
            document: str
            query:    str
            length:   int
            Builds snippet of a given length
        '''

        #prepare data
        sentences = document.sentences
        lines = [self.normalize(x.decode("utf-8")) for x in sentences]
        query = self.normalize(query.decode("utf-8").strip())

        #compute rank of each sencence
        rank = np.zeros(len(lines))
        for i in xrange(len(lines)):
            for j in xrange(len(query)):
                rank[i] += lines[i].count(query[j])

        #select sentences based on their rank
        ranked = list(np.argsort(rank))[::-1]
        sent_sel = []
        len_sel = 0
        cnt_sel = 0
        while cnt_sel < len(ranked) and len_sel + len(sentences[ranked[cnt_sel]]) <= length:
            sent_sel.append(ranked[cnt_sel])
            len_sel += len(sentences[ranked[cnt_sel]])
            cnt_sel += 1
        sent_sel = sorted(sent_sel)

        #concatenate selected sentences
        snippet = ''
        for i in xrange(len(sent_sel)):
            if i != 0 and sent_sel[i] != sent_sel[i-1]+1:
                #concatenate sentences that aren't near
                if snippet[-1] in self.SPEC:
                    snippet = snippet[:-1] + " " + self.TDOT
                else:
                    snippet = snippet + " " + self.TDOT
            snippet += ' ' + sentences[sent_sel[i]].strip()

        #enrich snippet by bolding query words
        snippet_rich = snippet
        for word in snippet.split():
            if self.norm(word.decode("utf-8")) in query:
                snippet_rich += "<b>" + word + "</b>"
            else:
                snippet_rich += word

        return snippet_rich

