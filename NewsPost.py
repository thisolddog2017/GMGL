class NewsPost(object):
    """docstring for NewsPost"""
    def __init__(self):
        super(NewsPost, self).__init__()

    def __str__(self):
        return "date: %s, day_of_the_week: %s, issue_number: %s, category_list: %s"%(self.date, self.day_of_the_week, self.issue_number, self.category_list)

    date = 0
    day_of_the_week = 0
    issue_number = 0
    category_list = []
