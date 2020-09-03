# -*- coding: utf-8 -*-
"""
Input Format
============

<MM>.<DD>

1. Lorem ipsum dolor sit amet, consectetur adipiscing elit

sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Vestibulum sed arcu non odio euismod. At elementum eu facilisis sed. Vehicula ipsum a arcu cursus vitae congue. Purus gravida quis blandit turpis.

2. Sed nisi lacus sed viverra

Porta lorem mollis aliquam ut porttitor leo. Eu sem integer vitae justo eget magna fermentum iaculis. Tincidunt dui ut ornare lectus sit amet est placerat in. Nulla porttitor massa id neque. Orci ac auctor augue mauris augue neque. Nunc aliquet bibendum enim facilisis. Nulla porttitor massa id neque aliquam. Aenean euismod elementum nisi quis eleifend quam adipiscing vitae proin. Nisl nunc mi ipsum faucibus.

3. Et molestie ac feugiat sed lectus vestibulum mattis ullamcorper velit

Pellentesque pulvinar pellentesque habitant morbi tristique. A diam sollicitudin tempor id eu nisl nunc mi. Et ligula ullamcorper malesuada proin libero nunc consequat interdum. Ipsum dolor sit amet consectetur adipiscing elit pellentesque habitant. Duis convallis convallis tellus id interdum velit laoreet id. Tellus elementum sagittis vitae et leo duis ut. Vitae et leo duis ut. Ultrices neque ornare aenean euismod elementum nisi quis. Viverra adipiscing at in tellus integer feugiat scelerisque.

NOTE
====

* <MM>.<DD> can be omitted, in which case the current date in UTC+8 is used
* each bullet starts with a number and a period followed by a single space - do not use Chinese punctuations!
* paragraphs don't support newlines at the moment
"""

import re
from NewsItem import NewsItem

bullet_start = r'([0-9]+)[.、][ ]?(.*?)(?<!。)$'
newlines_or_whitespace = r'[\r\n]+[\r\n\s]*'
itempat = re.compile(r'{}{}((?:(?!{})[^\r\n])+)?'.format(
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
