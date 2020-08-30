# -*- coding: utf-8 -*-
"""
Format of the input
===================

<MM>.<DD>

1. Lorem ipsum dolor sit amet, consectetur adipiscing elit

sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Vestibulum sed arcu non odio euismod. At elementum eu facilisis sed. Vehicula ipsum a arcu cursus vitae congue. Purus gravida quis blandit turpis.

2. Lorem ipsum dolor sit amet, consectetur adipiscing elit

sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Vestibulum sed arcu non odio euismod. At elementum eu facilisis sed. Vehicula ipsum a arcu cursus vitae congue. Purus gravida quis blandit turpis.

3. Lorem ipsum dolor sit amet, consectetur adipiscing elit

sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Vestibulum sed arcu non odio euismod. At elementum eu facilisis sed. Vehicula ipsum a arcu cursus vitae congue. Purus gravida quis blandit turpis.

4. Lorem ipsum dolor sit amet, consectetur adipiscing elit

sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Vestibulum sed arcu non odio euismod. At elementum eu facilisis sed. Vehicula ipsum a arcu cursus vitae congue. Purus gravida quis blandit turpis.

NOTE
====

* the <month>.<day> can be omitted, in which case the current date in UTC+8 is used
* paragraphs don't support newlines at the moment
"""

import re
from NewsItem import NewsItem

itempat = re.compile(r'([0-9]+). ([^\r\n]+)[\r\n]+([^\r\n]+)')

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
        NewsItem('{}. {}'.format(i, m.group(2)), m.group(3))
        for i, m in enumerate(itempat.finditer(content), start=1)
    ]
    # TODO use better interface to handle date / category etc. parameters
    if not items:
        raise ValueError("No news items detected, check your input!")
    for i in items:
        i.category = 'all'

    return post, items
