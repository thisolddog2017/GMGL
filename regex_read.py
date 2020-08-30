# -*- coding: utf-8 -*-

import re
from NewsItem import NewsItem

pat = re.compile(r'([0-9]+). ([^\n]+)\n\n([^\n]+)')

def read_news_items(content):
    '''Read from content string and extract the list of news

    Return a list of NewsItem
    '''
    # group(1): number # ignore
    # group(2): title
    # group(3): content
    return [
        NewsItem('{}. {}'.format(i, m.group(2)), m.group(3))
        for i, m in enumerate(pat.finditer(content), start=1)
    ]
