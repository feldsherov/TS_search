#!/usr/bin/env python

# -*- coding: utf-8 -*-
import optparse
import pymorphy2
import shelve
import copy

from index_builder import Sentence

__author__ = 'feldsherov'

morph = pymorphy2.MorphAnalyzer()


def get_query_words(query):
    global morph
    words = query.split(" ")
    return [morph.parse(word)[0].normal_form for word in words if word != ""]


class SnippetBuilder:
    def __init__(self, index_path):
        self.index_shlv = shelve.open(index_path, "r")

    @staticmethod
    def get_revelatory(sentence, q_words):
        return 100 * sentence.get_words_intersection(q_words) + \
                len(sentence.text) - sentence.position

    @staticmethod
    def form_snippet_by_sentences(sentences):
        sentences.sort(key=lambda snt: snt.position)

        ans, cp = [sentences[0].text], 1
        while cp < len(sentences):
            if ans[-1].position + 1 < sentences[cp]:
                ans[-1] += "..."
            ans.append(sentences[cp].text)

        return "".join(ans)

    def get_snippet(self, pt, query, nes_size):
        sentences = self.index_shlv[pt]

        if len(sentences) == 0:
            return "I can't build snippet. Too less text in document."

        q_words = get_query_words(query)
        sentences.sort(key=lambda sentence: -SnippetBuilder.get_revelatory(sentence, q_words))

        snippet_sentences, csize, cp = list(), 0, 0
        while csize < nes_size and cp < len(sentences):
            csize += len(sentences[cp].words)
            snippet_sentences.append(sentences[cp])
            cp += 1

        ans = SnippetBuilder.form_snippet_by_sentences(snippet_sentences)
        return ans

    def __del__(self):
        self.index_shlv.close()


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-i", "--index",
                      action="store",
                      dest="index_path",
                      type="string",
                      default="./index",
                      help="right index")
    parser.add_option("-f", "--file",
                      action="store",
                      dest="file",
                      type="string",
                      help="file for creating snippet")
    parser.add_option("-q", "--query",
                      action="store",
                      type="string",
                      dest="query",
                      help="search query")
    parser.add_option("-s", "--size",
                      action="store",
                      type="int",
                      dest="size",
                      default=10,
                      help="size of snippet in words")

    options, args = parser.parse_args()

    if not options.file:
        parser.error('File for snippet not given')

    if not options.query:
        parser.error("Query not given")

    print "Use index: %s" % options.index_path
    print "Build snippet for file %s and query %s" % (options.file, options.query)

    snippet_builder = SnippetBuilder(options.index_path)
    options.query = bytes(options.query).decode("utf-8")
    print "Snippet: %s" % snippet_builder.get_snippet(options.file, options.query, options.size)