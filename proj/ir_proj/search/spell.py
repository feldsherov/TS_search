#coding: utf-8
from math import log
import numpy as np
import time
import os.path

###EXAMPLE#####################################
# from spell import Spell                     #
# sp = Spell('data/words.num', tolerance=10)  #
# sp.test()                                   #
# print sp.spell(u'привте. как дела?')        #
###############################################


__author__ = 'danpol'
__version__ = 0.2


class Spell:
    _end = '_end_'

    @staticmethod
    def make_trie(words):
        root = dict()
        for word in words:
            current_dict = root
            for letter in word:
                current_dict = current_dict.setdefault(letter, {})
            current_dict[Spell._end] = [word]
        return root

    def __init__(self, words_filename, tolerance=10):
        self.eng = u"`qwertyuiop[]asdfghjkl;'zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:\"ZXCVBNM<>?"
        self.rus = u"]йцукенгшщзхъфывапролджэячсмитьбю.[!\"№;%:?*()_+ЙЦУКЕНГШЩЗХЪ/ФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,"
        self.letters_rus = u'-йцукенгшщзфывапролдячсмитьбюэёъ'
        self.letters_eng = u'-qwertyuiopasdfghjklzxcvbnm'
        self.e2r = {x[0]: x[1] for x in zip(self.eng, self.rus)}
        self.r2e = {x[0]: x[1] for x in zip(self.rus, self.eng)}
        w = map(lambda x: x.split(), open(words_filename).readlines())
        self.words = dict(map(lambda x: (x[1].decode('utf-8').lower(), log(float(x[2].strip())+1)), w))
        self.allwords = set(self.words.keys())
        self.tolerance = tolerance
        self.nearwords = Spell.make_trie(self.allwords)

    @staticmethod
    def dist(a, b, rt=False):
        demp = 0.4
        d = np.zeros((len(a)+1, len(b)+1), dtype=float)
        for i in range(len(a)+1):
            for j in range(len(b)+1):
                if min(i, j) == 0:
                    d[i, j] = max(i, j)
                elif i > 1 and j > 1:
                    d[i, j] = min(d[i-1, j]+1-demp*int(a[i-1] == a[i-2]),
                                  d[i, j-1]+1-demp*int(b[j-1] == b[j-2]),
                                  d[i-1, j-1]+int(a[i-1] != b[j-1]))
                    if a[i-1] == b[j-2] and a[i-2] == b[j-1]:
                        d[i, j] = min(d[i-2, j-2]+1, d[i, j])
                else:
                    d[i, j] = min(d[i-1, j]+1,
                                  d[i, j-1]+1,
                                  d[i-1, j-1]+int(a[i-1] != b[j-1]))
        if rt:
            return d
        return d[-1, -1]

    def switch(self, a):
        #a = unicode(a)
        return u''.join(map(lambda x: self.e2r[x] if x in self.e2r else self.r2e.get(x, x), a))

    @staticmethod
    def tolower(a):
        return a.lower(), map(lambda x: unicode.islower(x), a)

    @staticmethod
    def fromlower(a, reg):
        return u''.join(map(lambda x: x[0].upper() if not x[1] else x[0], zip(a, reg)))

    def candidates(self, word, root, depth):
        if len(root) == 0:
            return list()
        res = list()
        if depth != 0:
            #let's do an error

            #deletion error
            if len(word) != 0:
                res += self.candidates(word[1:], root, depth-1)

            #insertion extra letter
            for l in self.letters_rus:
                res += self.candidates(word, root.get(l, {}), depth-1)

            #replacement
            for l in self.letters_rus:
                res += self.candidates(word[1:], root.get(l, {}), depth-1)

            #swap
            if len(word) >= 2:
                res += self.candidates(word[1] + word[0] + word[2:], root, depth-1)
        if len(word) != 0:
            res += (self.candidates(word[1:], root.get(word[0], {}), depth))
        else:
            res += (root.get(Spell._end, []))
        return res

    def prob(self, w_given, w_asumed, additional_distance=0):
        # p(w | w') ~ p(w' | w) * p(w) --> assume uniform distribution
        return self.tolerance**(-Spell.dist(w_given, w_asumed)-additional_distance)*self.words.get(w_asumed, 0.00001)

    def closest(self, w, letters, add=0, depth=2):
        t = time.time()
        cnd = set(self.candidates(w, self.nearwords, depth)) & self.allwords | {w}
        pb = lambda x: self.prob(w, x, add)
        res = max(cnd, key=pb)
        return [pb(res), res]

    def match_reg(self, w1, w2):
        a = w1.lower()
        b = w2.lower()
        #print w1
        #print w2
        d = np.zeros((len(a)+1, len(b)+1), dtype=float)
        for i in range(len(a)+1):
            for j in range(len(b)+1):
                if min(i, j) == 0:
                    d[i, j] = max(i, j)
                elif i > 1 and j > 1 and a[i-1] == b[j-2] and a[i-2] == b[j-1]:
                    d[i, j] = min(d[i-1, j]+1,
                                  d[i, j-1]+1,
                                  d[i-1, j-1]+int(a[i-1] != b[j-1]),
                                  d[i-2, j-2]+1)
                else:
                    d[i, j] = min(d[i-1, j]+1,
                                  d[i, j-1]+1,
                                  d[i-1, j-1]+int(a[i-1] != b[j-1]))
        #print d
        i, j = d.shape
        i -= 1
        j -= 1
        res = ''
        while i > 0 or j > 0:
            if i != 0 and d[i-1, j]+1 == d[i, j]:
                #deleted
                i -= 1
            elif d[i, j-1]+1 == d[i, j]:
                #inserted
                if w1[i-1].isupper():
                    res += w2[j-1].upper()
                else:
                    res += w2[j-1]
                j -= 1
            elif j != 0 and d[i-1, j-1]+int(a[i-1] != b[j-1]) == d[i, j]:
                #replaced
                if w1[i-1].isupper():
                    res += w2[j-1].upper()
                else:
                    res += w2[j-1]
                i -= 1
                j -= 1
            else:
                res += w1[i-2]+w1[i-1]
                i -= 2
                j -= 2
        return res[::-1]

    def spell_word(self, w, depth=2):
        W = w
        w = w.lower()
        res = self.closest(w, self.letters_rus, depth=depth)
        res[1] = self.match_reg(W, res[1])
        return res

    def gen_candidates(self, w):
        res = []
        for i in xrange(len(w)):
            res += [(w[:i]+' '+w[i:], 4)]
            if w[i] == ' ':
                res += [(w[:i]+w[i+1:], 5)]
        res += [(self.switch(w), 2)]
        return res + [(w, 0)]

    def spell(self, w):
        w = unicode(w)
        w = u''.join(map(lambda x: x, w))
        max_res = ''
        max_prob = 0
        for cand in self.gen_candidates(w):
            r = reduce(lambda x, y: (x[0]*y[0], x[1]+' '+y[1]), [self.spell_word(x, 1 + int(cand[1] == 0)) for x in cand[0].split()])
            if r[0]*self.tolerance**(-cand[1]) > max_prob:
                max_prob = r[0]*self.tolerance**(-cand[1])
                max_res = r[1]
        return max_res

    def test(self, verbose=True):
        words = [u'прИвте', u'куица', u'z,kjrj', u'вкуснополезно', u'куреца', u'курассан', u'ghbju', u'эксплуатироват',
                 u'привЕ', u'Ривет', u'АнаСемИнович', u'пицц', u'ана']
        targt = [u'прИвет', u'курица', u'яблоко', u'вкусно полезно', u'курица', u'круассан', u'пирог', u'эксплуатировать',
                 u'привЕТ', u'пРивет', u'Анна СемЕнович', u'пицца', u'анна']
        f = True
        for w, t in zip(words, targt):
            tm = time.time()
            r = self.spell(w)
            tm = time.time()-tm
            if r != t:
                if verbose:
                    print(u'Should be {} from {}, got {} ({}s) [FAIL]'.format(t, w, self.spell(w), tm))
                f = False
            else:
                if verbose:
                    print(u'Should be {} from {}, got {} ({}s) [OK]'.format(t, w, self.spell(w), tm))
        if f:
            print('-----[OK]-----')
        else:
            print('-----[FAIL]-----')
        return f
