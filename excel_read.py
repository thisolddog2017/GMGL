# -*- coding: utf-8 -*-
 
import xlrd
import datetime
from NewsPost import NewsPost
from NewsItem import NewsItem



excel_dict = {
    "news_category" : "news_category",
    "news_title" : "news_title",
    "news_content" : "news_content",
    "url" : "url",
    "date" : "date(yyyy/mm/dd)",
    "issue_number" : "issue_number",
}


def excel_data(file= 'data.xls', sheet_index=-1):
    
    try:
        data = xlrd.open_workbook(file)
        sheet = data.sheet_by_index(sheet_index)
        nrows = sheet.nrows
        ncols = sheet.ncols
        if nrows <= 1:
            print("Please input data in the excel.")
            return 0
        else:
            post = NewsPost()

            date_col_num = find_col_num(sheet, excel_dict['date'])
            if not detect_empty(sheet, date_col_num):
                post.date = xlrd.xldate.xldate_as_datetime(sheet.cell(1, date_col_num).value, data.datemode)
                post.day_of_the_week = xlrd.xldate.xldate_as_datetime(sheet.cell(1, date_col_num).value, data.datemode).weekday()
            
            issue_number_col_num = find_col_num(sheet, excel_dict['issue_number'])
            if detect_empty(sheet, issue_number_col_num):
                post.issue_number = 0
            else:
                post.issue_number = int(sheet.cell(1, issue_number_col_num).value)

            news_item_list = []
            category_col_num = find_col_num(sheet, excel_dict['news_category'])

            post.category_list = []
            for row in range(1, nrows):
                news_item = NewsItem()
                if detect_empty(sheet, category_col_num):
                    post.category_list = ['all']
                    news_item.category = 'all'
                else:
                    category = sheet.cell(row, category_col_num).value
                    if category not in post.category_list:
                        post.category_list.append(category)
                    news_item.category = category
                #news_item.category = 'all' if detect_empty(sheet, category_col_num) else category
                if not detect_empty(sheet, find_col_num(sheet, excel_dict['news_title'])):
                    news_item.title = sheet.cell(row, find_col_num(sheet, excel_dict['news_title'])).value
                if not detect_empty(sheet, find_col_num(sheet, excel_dict['news_content'])):
                    news_item.content = sheet.cell(row, find_col_num(sheet, excel_dict['news_content'])).value
                if not detect_empty(sheet, find_col_num(sheet, excel_dict['url'])):
                    news_item.url = sheet.cell(row, find_col_num(sheet, excel_dict['url'])).value
                news_item_list.append(news_item)
        return post, news_item_list
    except Exception as e:
        print(e)

def find_col_num(sheet, col_name):
    for col in range(sheet.ncols):
        if col_name == sheet.cell_value(0, col):
            return col
    return None

def detect_empty(sheet, col_num):
    if col_num == None:
        return True
    elif "" == sheet.cell_value(1, col_num):
        return True
    else:
        return False

if __name__ == "__main__":
    post, news_item_list = excel_data()
    for item in news_item_list:
        print(item)
    print(post, news_item_list)