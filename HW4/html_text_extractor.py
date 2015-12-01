#!/usr/bin/env python
import re
import string
from bs4 import BeautifulSoup


__author__ = 'feldsherov'


class HTMLTextExtractor:
    def __init__(self, skip_tags=('script', 'style', 'noindex')):
        self.skip_tags = skip_tags
        pass

    def extract(self, markup):
        soup = BeautifulSoup(markup, 'lxml')

        for el in soup.find_all(self.skip_tags):
            el.decompose()

        text = soup.get_text()
        for sp in string.whitespace:
            text = re.sub("[%s]+" % sp, sp, text)
        return text