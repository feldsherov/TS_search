#!/usr/bin/env python
__author__ = 'feldsherov'


class VarByte:
    def __init__(self):
        pass

    @staticmethod
    def encode(lst):
        lst = [0] + [int(i) for i in lst]
        d = list()
        for i in range(1, len(lst)):
            d.append(lst[i] - lst[i - 1])

        code = list()
        for el in d:
            cp = 0
            while el >= 128:
                cp += 1
                code.append(chr(el % 128))
                el /= 128
            code.append(chr(el + 128))

        return "".join(code)

    @staticmethod
    def decode(r):
        d = list()
        cp = 0
        st = list()
        while cp < len(r):
            el = 0
            while ord(r[cp]) < 128:
                st.append(ord(r[cp]))
                cp += 1
            st.append(ord(r[cp]) - 128)

            while len(st):
                el *= 128
                el += st[-1]
                st.pop()

            d.append(el)
            cp += 1

        cv = 0
        ans = list()
        for el in d:
            ans.append(el + cv)
            cv += el

        return ans