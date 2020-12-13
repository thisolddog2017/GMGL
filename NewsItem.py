class NewsItem(object):
    """docstring for NewsItem"""
    def __init__(self, title=None, content=None):
        super(NewsItem, self).__init__()
        self.title = title or ''
        self._title_markdown = None
        self.content = content or ''
        self.url = ''
        self.category = ''
        self._content_markdown = None

    def __str__(self):
        return "title: %s, content: %s, url: %s, category: %s"%(self.title, self.content, self.url, self.category)

    @property
    def content_markdown(self):
        return self._content_markdown or self.content

    @content_markdown.setter
    def content_markdown(self, value):
        self._content_markdown = value

    @property
    def title_markdown(self):
        return self._title_markdown or self.title

    @title_markdown.setter
    def title_markdown(self, value):
        self._title_markdown = value
