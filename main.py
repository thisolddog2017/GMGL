# -*- coding: utf-8 -*-
import os
import re
from PIL import Image, ImageFont, ImageDraw
import datetime
import text_to_image
import configparser
import traceback
import shutil



# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')


cfg = {
    "header": config.get('path', 'header'),
    "category": config.get('path', 'category'),
    "footer": config.get('path', 'footer'),
    "temp_dir": config.get('path', 'temp_dir'),
    "out_dir": config.get('path', 'out_dir'),

    "date_enabled": config.getboolean('date', 'enabled'),
    "date_font_name": config.get('date', 'font-name'),
    "date_font_color": tuple(eval(config.get('date', 'font-color'))),
    "date_font_size": config.getint('date', 'font-size'),
    "date_line_height": config.getint('date', 'line-height'),
    "date_format": config.get('date', 'format'),
    "date_square_xy": tuple(eval(config.get('date', 'square-xy'))),
    "date_square_width": config.getint('date', 'square-width'),
    "date_square_height": config.getint('date', 'square-height'),
    
    "day_of_the_week_enabled": config.getboolean('day_of_the_week', 'enabled'),
    "day_of_the_week_font_name": config.get('day_of_the_week', 'font-name'),
    "day_of_the_week_font_color": tuple(eval(config.get('day_of_the_week', 'font-color'))),
    "day_of_the_week_font_size": config.getint('day_of_the_week', 'font-size'),
    
    "issue_number_enabled": config.getboolean('issue_number', 'enabled'),
    "issue_number_font_name": config.get('issue_number', 'font-name'),
    "issue_number_font_color": tuple(eval(config.get('issue_number', 'font-color'))),
    "issue_number_font_size": config.getint('issue_number', 'font-size'),
    
    "category_enabled": config.getboolean('category', 'enabled'),
    "category_font_name": config.get('category', 'font-name'),
    "category_font_color": tuple(eval(config.get('category', 'font-color'))),
    "category_font_size": config.getint('category', 'font-size'),
    "category_square_xy": tuple(eval(config.get('category', 'square-xy'))),
    "category_square_width": config.getint('category', 'square-width'),
    "category_square_height": config.getint('category', 'square-height'),
    
    "quality": config.getint('general', 'quality'),
    
    "easter_egg":config.getboolean('miscellaneous', 'easter_egg')
}
post_cfg = {
    "images_dir": config.get('path', 'images_dir'),
    "fonts_dir": config.get('path', 'fonts_dir'),
    "width": config.getint('general', 'width'),
    "pattern_enabled": config.getboolean('pattern', 'enabled'),
    "pattern": config.get('path', 'pattern'),
    "padding": tuple(eval(config.get('general', 'padding'))),
    "background_color": tuple(eval(config.get('general', 'background-color'))),
    "break_word": config.getboolean('general', 'break-word')
}
news_item_title_cfg = {
    "line_height": config.getint('news_title', 'line-height'),
    "font_size": config.getint('news_title', 'font-size'),
    "font_family": config.get('news_title', 'font-family'),
    "font_color": tuple(eval(config.get('news_title', 'font-color')))
}
news_item_content_cfg = {
    "line_height": config.getint('news_content', 'line-height'),
    "font_size": config.getint('news_content', 'font-size'),
    "font_family": config.get('news_content', 'font-family'),
    "font_color": tuple(eval(config.get('news_content', 'font-color')))
}
news_url_cfg = {
    "url_enabled": config.getboolean('url', 'enabled'),
    "line_height": config.getint('url', 'line-height'),
    "font_size": config.getint('url', 'font-size'),
    "font_family": config.get('url', 'font-family'),
    "font_color": tuple(eval(config.get('url', 'font-color')))
}

header_image_path=(os.path.join(post_cfg['images_dir'], cfg['header']))
category_image_path=(os.path.join(post_cfg['images_dir'], cfg['category']))
footer_image_path=(os.path.join(post_cfg['images_dir'], cfg['footer']))


def read_post_and_news_items_from_excel():
    '''NOTE: assumes that the relevant configs & modules are present'''
    # data=data.xls
    # sheet_index=-1
    data = config.get('path', 'data')
    sheet_index = config.getint('path', 'sheet_index')
    import excel_read
    return excel_read.excel_data(data, sheet_index)


def generate_image(post, news_items):
    '''post : a NewsPost
    news_items : list of NewsItem

    returns the path to output image, if success
    '''
    try:
        for p in [cfg['temp_dir'], cfg['out']]:
            if not os.path.exists(p):
                os.makedirs(p)
        shutil.copyfile(header_image_path,append_temp_dir("header.temp.png"))
        if cfg['date_enabled']:
            header_date_square_xy = align_center_in_box(date_text, cfg["date_font_name"], cfg["date_font_size"], cfg["date_square_xy"], cfg["date_square_width"], cfg["date_square_height"])
            timestamping(append_temp_dir("header.temp.png"), append_temp_dir("header.temp.png"), header_date_square_xy, cfg["date_font_name"], cfg["date_font_color"], cfg["date_font_size"], date_text)
        if cfg['day_of_the_week_enabled']:
            header_dow_xy = align_center_in_context(weekday_dict[post.day_of_the_week], cfg["day_of_the_week_font_name"], cfg["day_of_the_week_font_size"], cfg["date_font_name"], cfg["date_font_size"], header_date_square_xy, date_text, cfg["date_line_height"])
            timestamping(append_temp_dir("header.temp.png"), append_temp_dir("header.temp.png"), header_dow_xy, cfg["day_of_the_week_font_name"], cfg["day_of_the_week_font_color"], cfg["day_of_the_week_font_size"], weekday_dict[post.day_of_the_week])
        if (cfg['issue_number_enabled']) & (post.issue_number != 0):
            issue_number_text = "第"+str(post.issue_number)+"期"
            header_issue_number_xy = align_center_in_context(issue_number_text, cfg["issue_number_font_name"], cfg["issue_number_font_size"], cfg["day_of_the_week_font_name"], cfg["day_of_the_week_font_size"], header_dow_xy, weekday_dict[post.day_of_the_week], cfg["date_line_height"])
            timestamping(append_temp_dir("header.temp.png"), append_temp_dir("header.temp.png"), header_issue_number_xy, cfg["issue_number_font_name"], cfg["issue_number_font_color"], cfg["issue_number_font_size"], issue_number_text)
        images.append(append_temp_dir("header.temp.png"))

        for idx in range(len(post.category_list)) :
            if cfg['category_enabled'] and post.category_list!=['all']:
                category_xy = align_center_in_box(post.category_list[idx], cfg["category_font_name"], cfg["category_font_size"], cfg["category_square_xy"], cfg["category_square_width"], cfg["category_square_height"])
                image_category(category_image_path, append_temp_dir('category'+str(idx)+'.temp.png'), category_xy, cfg["category_font_name"], cfg["category_font_color"], cfg["category_font_size"], post.category_list[idx])
                images.append(append_temp_dir('category'+str(idx)+'.temp.png'))
            for i in range(len(news_item_list)):
                if news_item_list[i].category == post.category_list[idx]:
                    if news_item_list[i].title != '':
                        text_to_image.image_generate_from_text(news_item_list[i].title, append_temp_dir("news_content.category"+str(idx)+".title"+str(i)+".temp.png"), news_item_title_cfg, post_cfg)
                        images.append(append_temp_dir("news_content.category"+str(idx)+".title"+str(i)+".temp.png"))
                    if news_item_list[i].content != '':
                        text_to_image.image_generate_from_text(news_item_list[i].content, append_temp_dir("news_content.category"+str(idx)+".content"+str(i)+".temp.png"), news_item_content_cfg, post_cfg)
                        images.append(append_temp_dir("news_content.category"+str(idx)+".content"+str(i)+".temp.png"))
                    if news_item_list[i].url != '' and news_url_cfg["url_enabled"]:
                        text_to_image.image_generate_from_text(news_item_list[i].url, append_temp_dir("news_content.category"+str(idx)+".url"+str(i)+".temp.png"), news_url_cfg, post_cfg)
                        images.append(append_temp_dir("news_content.category"+str(idx)+".url"+str(i)+".temp.png"))

        images.append(footer_image_path)
        out_path = "{}/早报{}.png".format(
            cfg['out_dir'],
            post.date.strftime("%Y.%m.%d")+'.png'),
            cfg['quality']
        )
        image_combine(
            images,
            out_path
        )
        # cleaning
        for image in images:
            if "temp" in image:
                os.remove(image)
        os.rmdir(cfg['temp_dir'])
        return out_path
    except Exception as e:
        print(repr(e))
        traceback.print_tb(e.__traceback__)
        input()

#dict, post.category_list
#date_text = dict['date'].strftime('%Y{0}%m{1}%d{2}').format(*'年月日')
date_text = post.date.strftime(cfg['date_format']).format(*'年月日').replace('X0','X').replace('X','')
images = []
weekday_dict = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}

# Timestamp on header

def timestamping(image_path, out_path, xy, font_path, font_color, font_size, text):
    im = Image.open(image_path)
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(os.path.join(post_cfg['fonts_dir'], font_path), font_size)
    draw.text(xy, text, font=font, fill=font_color)
    im.save(out_path)
    return out_path

# Generate news
# Align center
def align_center_in_context(text, font_name, font_size, last_line_font_name, last_line_font_size, last_line_xy, last_line_text, line_height):
    last_line_font = ImageFont.truetype(os.path.join(post_cfg['fonts_dir'], last_line_font_name), last_line_font_size)
    last_line_font_width, last_line_font_height = last_line_font.getsize(last_line_text)
    
    font = ImageFont.truetype(os.path.join(post_cfg['fonts_dir'], font_name), font_size)
    font_width, font_height = font.getsize(text)
    xy_offset = ((last_line_font_width - font_width)/2 , line_height)
    xy = tuple(map(lambda x: x[0]+x[1], zip(last_line_xy, xy_offset)))
    return xy

def align_center_in_box(text, font_name, font_size, category_square_xy, category_square_width, category_square_height):
    font = ImageFont.truetype(os.path.join(post_cfg['fonts_dir'], font_name), font_size)
    font_width, font_height = font.getsize(text)
    xy_offset = ((category_square_width - font_width)/2 , (category_square_height - font_height)/2)
    xy = tuple(map(lambda x: x[0]+x[1], zip(category_square_xy, xy_offset)))
    return xy

## Category image
def image_category(image_path, out_path, xy, font_path, font_color, font_size, text):
    im = Image.open(image_path)
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(os.path.join(post_cfg['fonts_dir'], font_path), font_size)
    draw.text(xy, text, font=font, fill=font_color)
    im.save(out_path)
    return out_path


# Combine images
def image_combine(images, out_path, quality):
    height = 0
    ims = []
    height_ims = []
    height_ims_offset = []
    width = Image.open(images[0]).size[0]
    for i in range(len(images)):
        ims.append(Image.open(images[i]))
        height_ims.append(Image.open(images[i]).size[1])
        height = height + Image.open(images[i]).size[1]
    result = Image.new(ims[0].mode, (width, height))

    for i in range(len(height_ims)):
        if i==0:
            height_ims_offset.append(0)
        else:
            sum = 0
            for j in range(i):
                sum = sum + height_ims[j]
            height_ims_offset.append(sum)
    for i, im in enumerate(ims):
        result.paste(im, box=(0, height_ims_offset[i]))
    if quality != 0:
        result.save(out_path, quality=quality)
    else:
        result.save(out_path)
    return out_path

def append_temp_dir(path):
    return os.path.join(cfg['temp_dir'], path)

if __name__ == "__main__":
    print("Good morning!")
    post, news_items = read_post_and_news_items_from_excel()
    out_path = generate_image(post, news_items)
    print("...and Good luck!")
    print(out_path)
