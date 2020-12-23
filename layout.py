import datetime

markdown_article_template = """---
templateKey: article
title: {title}
slug: zao-bao
date: {date:%Y-%m-%dT%H:%M:%SZ}
featuredpost: false
trending: 0
isbrief: true
contributors:
  - type: 作者
    name: {author_name}

---
{body}

欢迎加入NGOCN的Telegram频道：ngocn01

微信好友：njiqirenno2
"""

markdown_message_template = """*{title}*

{body}
"""

def post_title(post):
    return '{} N记早报'.format(post.date.strftime('%-m.%-d'))

def layout_text(post, items):
    '''Layout the parsed content in the standard text form'''
    lines = [post_title(post)]
    for i in items:
        if i.title:
            lines.append(i.title)
        if i.content:
            lines.append(i.content)
    return '\n\n'.join(lines)

class MarkdownArticle:
    def __init__(self, name, content):
        self.name = name
        self.content = content

def layout_markdown_body(post, items, title_format='*{}*'):
    lines = []
    for i in items:
        if i.title:
            lines.append(title_format.format(i.title_markdown))
        if i.content:
            lines.append(i.content_markdown)
    return '\n\n'.join(lines)

def layout_markdown_article(post, items, author_name):
    '''Layout the parsed content in the markdown article format'''
    body = layout_markdown_body(post, items, title_format='**{}**')

    name = post.date.strftime('%Y-%m-%d-zao-bao.md')
    content = markdown_article_template.format(
        title=post_title(post),
        date=datetime.datetime.utcnow(),
        body=body,
        author_name=author_name
    )
    return MarkdownArticle(name, content)

def layout_markdown_message(post, items):
    '''Layout the parsed content in Telegram compatible markdown format'''
    body = layout_markdown_body(post, items)
    return markdown_message_template.format(
        title=post_title(post),
        body=body,
    )
