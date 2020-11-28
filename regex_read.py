# -*- coding: utf-8 -*-
"""
早報輸入格式: https://github.com/thisolddog2017/GMGL-pub/wiki/%E6%97%A9%E5%A0%B1%E8%BC%B8%E5%85%A5%E6%A0%BC%E5%BC%8F
"""

import re
from NewsItem import NewsItem

bullet_start = r'([0-9]+)\. '
newlines_or_whitespace = r'[\r\n]+[\r\n\s]*'
itempat = re.compile(r'{}([^\r\n]+){}((?:(?!{})[^\r\n])+)?'.format(
    bullet_start,
    newlines_or_whitespace,
    bullet_start
), flags=re.MULTILINE)

class InvalidContent(ValueError):
    pass

class NoItems(InvalidContent):
    pass

def parse(content):
    '''Read from content string and extract the list of news

    Return (post, list of NewsItem)
    '''
    # first check if the date is present in the content input
    date_match = re.match(r'([01]?[0-9])\.([0-3]?[0-9])', content)
    if date_match:
        import datetime
        date = datetime.date(
            datetime.date.today().year,
            int(date_match.group(1)),
            int(date_match.group(2))
        )
        content = content[len(date_match.group(0)):]
    else:
        from datetime import datetime, timezone, timedelta
        date = datetime.today().replace(tzinfo=timezone.utc).astimezone(
            tz=timezone(timedelta(hours=8))
        )

    from NewsPost import NewsPost
    post = NewsPost()
    # TODO use better interface to handle date / category etc. parameters
    post.date = date
    post.category_list = ['all']

    # group(1): number # ignore
    # group(2): title
    # group(3): content
    items = [
        NewsItem(
            '{}. {}'.format(i, m.group(2) or '').strip(),
            (m.group(3) or '').strip()
        )
        for i, m in enumerate(itempat.finditer(content), start=1)
    ]
    # TODO use better interface to handle date / category etc. parameters
    if not items:
        raise NoItems()
    for i in items:
        i.category = 'all'

    return post, items

def lay_out(post, items):
    '''Layout the parsed content in the standard text form'''
    lines = ['{} N记早报'.format(post.date.strftime('%-m.%-d'))]
    for i in items:
        if i.title:
            lines.append(i.title)
        if i.content:
            lines.append(i.content)
    return '\n\n'.join(lines)
