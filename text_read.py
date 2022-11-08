# -*- coding: utf-8 -*-
"""
日報輸入格式: https://github.com/thisolddog2017/GMGL-pub/wiki/%E6%97%A9%E5%A0%B1%E8%BC%B8%E5%85%A5%E6%A0%BC%E5%BC%8F
"""

import re
from NewsItem import NewsItem
import markdown

class InvalidContent(ValueError):
    def __init__(self, line=''):
        self.line = line
    def quote_msg(self, msg):
        if self.line:
            return '\n'.join([
                msg,
                '```',
                self.line,
                '```'
            ])
        return msg

class EmptyTitle(InvalidContent):
    def __str__(self):
        return self.quote_msg("新聞標題不能爲空")

class TitleWithFormats(InvalidContent):
    def __str__(self):
        return self.quote_msg("新聞標題不能內置鏈接或格式")

class EmptyInput(InvalidContent):
    def __str__(self):
        return "無日報輸入？"

class NoItems(InvalidContent):
    def __str__(self):
        return "無日報新聞？"

class LeadingContentWithoutTitle(InvalidContent):
    def __str__(self):
        return self.quote_msg("未找到新聞標題——是否有放置加上數字的小標題？")

item_line_pat = re.compile(r'([0-9]+)\.(?P<title>( .*|))$')

def parse(content, content_markdown=None):
    # TODO simpler way
    post, items = _parse(content)
    if content_markdown:
        _, items_markdown = _parse(content_markdown)
        for i, im in zip(items, items_markdown):
            i.title_markdown = im.title
            i.content_markdown = im.content
    return post, items

def _parse(content):
    '''Read from content string and extract the list of news

    Return (post, list of NewsItem)
    '''
    lines = content.splitlines()
    if not lines:
        raise EmptyInput()

    # first check if the date is present in the content input
    date_match = re.match(r'([01]?[0-9])\.([0-3]?[0-9])', lines[0])
    if date_match:
        import datetime
        date = datetime.date(
            datetime.date.today().year,
            int(date_match.group(1)),
            int(date_match.group(2))
        )
        lines.pop(0)
    else:
        from datetime import datetime, timezone, timedelta
        date = datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=timezone(timedelta(hours=8))).date()

    from NewsPost import NewsPost
    post = NewsPost()
    # TODO use better interface to handle date / category etc. parameters
    post.date = date
    post.category_list = ['all']

    title_content_pairs = []
    current_item_title = None
    current_item_content_lines = []
    # pick number prefixed lines as start of each item
    while lines:
        # first line must match
        line = lines.pop(0)
        if not line.strip(): # whitespace
            continue
        m = item_line_pat.match(line)
        if m:
            if current_item_title:
                title_content_pairs.append((current_item_title, current_item_content_lines))
            title = m.group('title').strip()
            if not title:
                raise EmptyTitle(line)
            if markdown.markdown_to_plaintext(title) != title:
                raise TitleWithFormats(line)
            current_item_title = title
            current_item_content_lines = []
        else:
            if current_item_title:
                line = line.strip()
                if line:
                    current_item_content_lines.append(line)
            else:
                raise LeadingContentWithoutTitle(line)

    if current_item_title:
        title_content_pairs.append((current_item_title, current_item_content_lines))

    items = [
        NewsItem(
            '{}. {}'.format(i, title),
            '\n\n'.join(content_lines)
        )
        for i, (title, content_lines) in enumerate(title_content_pairs, start=1)
    ]

    # TODO use better interface to handle date / category etc. parameters
    if not items:
        raise NoItems()
    for i in items:
        i.category = 'all'

    return post, items

