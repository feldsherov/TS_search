#!/usr/bin/env python
__author__ = 'feldsherov'


def to_differences(numbers):
    lst = [0] + [int(i) for i in numbers]
    d = list()
    for i in range(1, len(lst)):
        d.append(lst[i] - lst[i - 1])

    return d


def to_sums(numbers):
    cv = 0
    ans = list()
    for el in numbers:
        ans.append(el + cv)
        cv += el

    return ans


def encode(lst, convert_to_differences=True):
    d = to_differences(lst) if convert_to_differences else lst

    code = list()
    for el in d:
        while el >= 128:
            code.append(chr(el % 128))
            el /= 128
        code.append(chr(el + 128))

    return "".join(code)


def decode(r, convert_to_sums=True):
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

    ans = to_sums(d) if convert_to_sums else d

    return ans