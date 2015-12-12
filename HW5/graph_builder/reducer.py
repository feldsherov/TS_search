#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys

from itertools import groupby
from operator import itemgetter

def read_mapper_output(file, separator='\t'):
    for line in file:
        yield line.rstrip().split(separator, 1)

def main():
    data = read_mapper_output(sys.stdin)
    for current_key, group in groupby(data, itemgetter(0)):
        cites = current_key
        cited = [cited for cites, cited in group]
        print "%s\t%s\t%s" % (cites, 0.15, " ".join(cited))

if __name__ == "__main__":
    main()
    