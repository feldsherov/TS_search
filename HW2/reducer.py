import zlib
import base64

from sys import stdin, stderr
from itertools import groupby
from operator import itemgetter
from varbyte import VarByte

__author__ = 'feldsherov'


def read_mapper_output(file_, separator='\t'):
    for line in file_:
        yield line.strip().split(separator, 1)


def main():
    data = read_mapper_output(stdin)
    for current_word, docs in groupby(data, itemgetter(0)):
        doc_ids = sorted(list(set(map(lambda a: int(itemgetter(1)(a)), docs))))
        print ("%s\t%s" %
                 (current_word.decode("unicode-escape").encode("utf8"),
                 base64.b64encode(VarByte.encode(doc_ids)))).strip()

if __name__ == "__main__":
    main()