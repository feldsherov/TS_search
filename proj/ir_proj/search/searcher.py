#!/usr/bin/python
import sys
import base64
from math import log
from Queue import heapq
import pymorphy2

from archiver import *

VARBYTE = 1
SIMPLE9 = 2

class Searcher:
    def __init__(self, index_filename, dict_filename, urls_filename, encoding=SIMPLE9):        
        self.index = open(index_filename, 'r')
        self.encoding = encoding
        
        
        if encoding != VARBYTE and encoding != SIMPLE9:
            raise Exception('Unknown encoding!')
        
        
        self.dictionary = {}
        for line in open(dict_filename, 'r'):
            word, pos = line.split("\t")
            self.dictionary[word.decode('utf-8')] = int(pos)
        
        self.urls = {}
        for line in open(urls_filename, 'r'):
            ind, url = line.split("\t")
            self.urls[int(ind)] = url.strip()
                        
        self.morph = pymorphy2.MorphAnalyzer()
        self.norm = lambda x: self.morph.parse(x)[0].normal_form
        self.N = len(self.urls)

    def search(self, query, return_length=100, passage_len=50, return_urls_only=False):
        '''
            Performs search on loaded data. 
            Returns list of sorted by rank:
              * tuples (url, rank) if return_urls_only == False
              * url                if return_urls_only == True
        '''
        query = query.strip()
        words = filter(lambda x: x != '', query.split(" "))
        result = None
        if len(words) == 0:
            return []
        word_index = [None] * len(words)
        for z, word in enumerate(words):
            word = self.norm(word.decode('utf-8').strip())
            if word in self.dictionary:
                self.index.seek(self.dictionary[word], 0)
                compressed = self.index.readline().strip()
                decompressed = None
                if self.encoding == VARBYTE:
                    decompressed = decode_varbyte(base64.b64decode(compressed))
                elif self.encoding == SIMPLE9:
                    decompressed = decode_simple9(base64.b64decode(compressed))
                decompressed, word_index[z] = from_flat(decompressed)
                if result == None:
                    result = decompressed
                else:
                    result = join(result, decompressed)
    
        k1 = 2
        b = 0.75
        if result == None or len(result) == 0:
            return []
           
        #Now we have a list of candidates. We apply BM25 to leave only return_length of them
        avg_len = 0.
        j = 0
        while word_index[j] == None:
            j += 1
            
        for i in xrange(len(result)):
            if result[i] in word_index[j]:
                avg_len += word_index[j][result[i]][0]
            
        avg_len /= len(result)
        BM25 = [0] * len(result)
        for j in xrange(len(words)):
            if word_index[j] != None:
                idf = log(float(self.N) / len(word_index[j]))
                for i in xrange(len(result)):
                    if result[i] in word_index[j]:
                        tf = float(len(word_index[j][result[i]][1])) / word_index[j][result[i]][0]
                        BM25[i] += tf * idf / (tf + k1 * (b + word_index[j][result[i]][0] / avg_len * (1 - b)))
        if len(result) > return_length:
            tpr = [(x, y) for x, y in zip(BM25, result)]
            heap = tpr[:return_length]
            heapq.heapify(heap)
            for rank, ind in tpr[return_length:]:
                if heapq.nsmallest(1, heap)[0][0] < rank:
                    heapq.heappop(heap)
                    heapq.heappush(heap, (rank, ind))
            result = [ind for rank, ind in heap]
        #Now we have a shortened list of candidates. We apply passage algorithm to leave top maxPASSpass
        scores = [0] * len(result)
        for i in xrange(len(result)):
            passage = []
            for j in xrange(len(words)):
                 if word_index[j] != None and result[i] in word_index[j]:
                        passage.extend([(x, j) for x in word_index[j][result[i]][1]])
            passage.sort()
            l = 0
            r = 0
            features = [0] * 5
            for l in xrange(len(passage)):
                for r in xrange(l, len(passage)):
                    if passage[r][0] - passage[l][0] + 1 > passage_len:
                        continue
                    passage_w = [x[1] for x in passage[l:r+1]]
                    features[0] = len(set([x[1] for x in passage[l:r+1]])) / float(len(words))
                    features[1] = 1 - float(passage[l][0]) / word_index[passage[l][1]][result[i]][0]
                    features[2] = 1 - float(r - l + 1) / (passage[r][0] - passage[l][0] + 1)
                               
                    features[3] = 0
                    for j in xrange(len(words)):
                        if word_index[j] != None:
                            idf = log(float(self.N) / len(word_index[j])) / log(self.N)
                            tf = float(passage_w.count(j)) / (passage[r][0] - passage[l][0] + 1)
                            features[3] += tf * idf
                    features[4] = 0
                    for j in xrange(len(passage_w)-1):
                        for k in xrange(j + 1, len(passage_w)):
                            if passage_w[j] > passage_w[k]:
                                features[4] += 1
                    if len(passage_w) != 1:
                        features[4] /= float(len(passage_w) * (len(passage_w) - 1) / 2)
                        
                    score = reduce(lambda x,y: x + y, features)
                    if score > scores[i]:
                        scores[i] = score
            
        final_result = []
        for score, url_id in sorted(zip(scores, result), reverse=True):
            final_result.append((self.urls[url_id], score))
        if return_urls_only:
            final_result = [x[0] for x in final_result]
        return final_result
        
    def __del__(self):
        self.index.close()            

