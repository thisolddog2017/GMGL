class NewsItem(object):
    """docstring for NewsItem"""
    def __init__(self):
        super(NewsItem, self).__init__()
    def __str__(self):
        return "title: %s, content: %s, url: %s, category: %s"%(self.title, self.content, self.url, self.category)


    title = ''
    content = ''
    url = ''
    category = ''