#!/usr/bin/env python
import struct
import sys


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


def zip_numbers(numbers, cbits):
    type_dict = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 7: 5, 9: 6, 14: 7, 28: 8}
    result_number = 0
    result_number |= (type_dict[cbits] << 28)

    for i, nm in enumerate(numbers):
        result_number |= (nm << (cbits * i))

    return struct.pack("i", result_number)


def unzip_numbers(number_as_bytes):
    bits_variants = (1, 2, 3, 4, 5, 7, 9, 14, 28)
    count_for_variants = (28, 14, 9, 7, 4, 3, 2, 1)

    number = (struct.unpack("i", number_as_bytes))[0]
    code_type = number >> 28
    cbits = bits_variants[code_type]
    cnumbers = count_for_variants[code_type]

    result_list = list()

    for i in range(cnumbers):
        result_list.append((number >> (i * cbits)) & ((1 << cbits) - 1))

    return result_list


def encode(lst, convert_to_differences=True):
    d = to_differences(lst) if convert_to_differences else lst

    cp = 0
    bits_variants = (1, 2, 3, 4, 5, 7, 9, 14, 28)
    count_for_variants = (28, 14, 9, 7, 4, 3, 2, 1)
    code = list()
    while cp < len(d):
        print >>sys.stderr, cp
        for cbits, c_cnt in zip(bits_variants, count_for_variants):
            sh = 0
            while cp + sh < len(d) and sh < c_cnt and d[cp + sh] < 2 ** cbits:
                sh += 1
                print >>sys.stderr, sh
            if sh == c_cnt:
                code.append(zip_numbers(d[cp: cp + sh], cbits))
                cp += sh
                break

    return "".join(code)


def decode(code, convert_to_sums=True):
    d = list()
    if len(code) % 4 != 0:
        raise ValueError("Len of simple9 code must be 4 * k")

    for cp in range(0, len(code), 4):
        d.extend(unzip_numbers(code[cp: cp + 4]))

    ans = to_sums(d) if convert_to_sums else d

    return ans

if __name__ == "__main__":
    nm = [1, 3, 4, 5, 6, 8, 9, 10, 11, 34, 54, 55, 56, 57, 58, 59, 60]
    code = encode(nm)
    print decode(code)