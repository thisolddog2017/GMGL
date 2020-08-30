#!/usr/bin/env python
# coding: utf-8


# -*- coding: utf-8 -*-
#
# Author: oldj
# Email: oldj.wu@gmail.com
# Blog: http://oldj.net
#

import os
import re
import sys
from PIL import Image
from PIL import ImageDraw, ImageFont


g_re_first_word = re.compile((""
    + "(%(prefix)s+\S%(postfix)s+)" # 标点
    + "|(%(prefix)s*\w+%(postfix)s*)" # 单词
    + "|(%(prefix)s+\S)|(\S%(postfix)s+)" # 标点
    + "|(\d+%%)" # 百分数
    ) % {
    "prefix": "['\"\(<\[\{‘“（《「『]",
    "postfix": "[:'\"\)>\]\}：’”）》」』,;\.\?!，、；。？！]",
}, re.A)


def getFont(font_family, font_size=14):
    return ImageFont.truetype(font_family, font_size)


def makeLineToWordsList(line, break_word=False):
    """将一行文本转为单词列表"""

    if break_word:
        return [c for c in line]

    lst = []
    while line:
        ro = g_re_first_word.match(line)
        end = 1 if not ro else ro.end()
        lst.append(line[:end])
        line = line[end:]
    return lst


def makeLongLineToLines(long_line, start_x, start_y, width, line_height, font, cn_char_width=0):
    """将一个长行分成多个可显示的短行"""

    txt = long_line
#    txt = u"测试汉字abc123"
#    txt = txt.decode("utf-8")

    if not txt:
        return [None]

    words = makeLineToWordsList(txt)
    lines = []

    if not cn_char_width:
        cn_char_width, h = font.getsize("汉")
    avg_char_per_line = width // cn_char_width
    if avg_char_per_line <= 1:
        avg_char_per_line = 1

    line_x = start_x
    line_y = start_y

    while words:

        tmp_words = words[:avg_char_per_line]
        tmp_ln = "".join(tmp_words)
        w, h = font.getsize(tmp_ln)
        wc = len(tmp_words)
        while w < width and wc < len(words):
            wc += 1
            tmp_words = words[:wc]
            tmp_ln = "".join(tmp_words)
            w, h = font.getsize(tmp_ln)
        while w > width and len(tmp_words) > 1:
            tmp_words = tmp_words[:-1]
            tmp_ln = "".join(tmp_words)
            w, h = font.getsize(tmp_ln)
            
        if w > width and len(tmp_words) == 1:
            # 处理一个长单词或长数字
            line_y = makeLongWordToLines(
                tmp_words[0], line_x, line_y, width, line_height, font, lines
            )
            words = words[len(tmp_words):]
            continue

        line = {
            "x": line_x,
            "y": line_y,
            "text": tmp_ln,
            "font": font,
        }

        line_y += line_height
        words = words[len(tmp_words):]

        lines.append(line)

        if len(lines) >= 1:
            # 去掉长行的第二行开始的行首的空白字符
            while len(words) > 0 and not words[0].strip():
                words = words[1:]
    return lines


def makeLongWordToLines(long_word, line_x, line_y, width, line_height, font, lines):

    if not long_word:
        return line_y

    c = long_word[0]
    char_width, char_height = font.getsize(c)
    default_char_num_per_line = width // char_width

    while long_word:

        tmp_ln = long_word[:default_char_num_per_line]
        w, h = font.getsize(tmp_ln)
        
        l = len(tmp_ln)
        while w < width and l < len(long_word):
            l += 1
            tmp_ln = long_word[:l]
            w, h = font.getsize(tmp_ln)
        while w > width and len(tmp_ln) > 1:
            tmp_ln = tmp_ln[:-1]
            w, h = font.getsize(tmp_ln)

        l = len(tmp_ln)
        long_word = long_word[l:]

        line = {
            "x": line_x,
            "y": line_y,
            "text": tmp_ln,
            "font": font,
            }

        line_y += line_height
        lines.append(line)
        
    return line_y


def makeMatrix(txt, font, text_cfg, img_cfg):

    width = img_cfg["width"]

    data = {
        "width": width,
        "height": 0,
        "lines": [],
    }

    a = txt.split("\n")
    cur_x = img_cfg["padding"][3]
    cur_y = img_cfg["padding"][0]
    cn_char_width, h = font.getsize("汉")

    for ln_idx, ln in enumerate(a):
        ln = ln.rstrip()
        f = font
        line_height = text_cfg["line_height"]
        current_width = width - cur_x - img_cfg["padding"][1]
        lines = makeLongLineToLines(ln, cur_x, cur_y, current_width, line_height, f, cn_char_width=cn_char_width)
        cur_y += line_height * len(lines)

        data["lines"].extend(lines)

    data["height"] = cur_y + img_cfg["padding"][2]

    return data


def makeImage(data, img_cfg):
    """
    """

    width, height = data["width"], data["height"]
    im = Image.new("RGB", (width, height), img_cfg["background_color"])
    dr = ImageDraw.Draw(im)

    for ln_idx, line in enumerate(data["lines"]):
        __makeLine(im, line, img_cfg)

    return im



def txt2im(txt, outfn, text_cfg, img_cfg, show=False):

    # cfg = makeConfig(cfg)
    font = getFont(os.path.join(img_cfg["fonts_dir"], text_cfg["font_family"]), text_cfg["font_size"])
    data = makeMatrix(txt, font, text_cfg, img_cfg)
    im = draw_text(data, text_cfg, img_cfg)
    if img_cfg['pattern_enabled']:
        pattern_im = Image.open(os.path.join(img_cfg['images_dir'], img_cfg['pattern']))
        paste_pattern(im, pattern_im)
    im.save(outfn)
    if os.name == "nt" and show:
        im.show()


def image_generate(text_path, out_path, text_cfg, img_cfg, show=False):
    c = open(text_path, "rb").read().decode("utf-8")
    txt2im(c, out_path, text_cfg, img_cfg, show)

def image_generate_from_text(text, out_path, text_cfg, img_cfg, show=False):
    txt2im(text, out_path, text_cfg, img_cfg, show)


def draw_text(data, text_cfg, img_cfg):
    width, height = data["width"], data["height"]
    im_without_justification = Image.new("RGB", (width, height), img_cfg["background_color"])
    #im_without_justification = makeImage(data, cfg)

    draw_without_justification = ImageDraw.Draw(im_without_justification)
    im = Image.new("RGB", (width, height), img_cfg["background_color"])
    draw = ImageDraw.Draw(im)
    padding_total = img_cfg["padding"][3] + img_cfg["padding"][1]
    for ln_idx, line in enumerate(data["lines"]):
        if not line:
            return
        x, y = line["x"], line["y"]
        text = line["text"]
        font = line["font"]
        draw_without_justification.text((x, y), text, fill=text_cfg["font_color"], font=font)

    for ln_idx, line in enumerate(data["lines"]):
        x, y = line["x"], line["y"]
        words = line["text"].split()
        font = line["font"]
        p = re.compile(r'([\u4e00-\u9fa5])')
        str_list = p.split(line["text"])
        words = [w for w in str_list if len(w.strip()) > 0]
        
        if (ln_idx == len(data["lines"]) - 1) or            len(words) == 1:
            draw.text((x, y), line["text"], fill=text_cfg["font_color"], font=font)
            continue
        line_without_spaces = ''.join(words)
        total_size = line["font"].getsize(line_without_spaces)
        space_width = (width - total_size[0] - padding_total) / (len(words) - 1.0)
        start_x = line["x"]
        original_x = line["x"]
        y = line["y"]

        for i in range(len(words)-1):
            word_size = line["font"].getsize(words[i])
            region = im_without_justification.crop((original_x,y,word_size[0]+original_x,text_cfg["line_height"]+y))
            im.paste(region, (int(start_x), int(y)))
            original_x += word_size[0]
            start_x += word_size[0] + space_width
        last_word_size = line["font"].getsize(words[-1])
        last_word_x = x + width - last_word_size[0] - padding_total
        region = im_without_justification.crop((original_x,y,last_word_size[0]+original_x,text_cfg["line_height"]+y))
        im.paste(region, (int(last_word_x), int(y)))      
        
    return im

def paste_pattern(im, pattern_im):
    """背景图粘帖"""
    width, height = im.size[0], im.size[1]

    height_left = height
    while height_left>0:
        im.paste(pattern_im,(0,height-height_left),mask=pattern_im)
        height_left-=pattern_im.size[1]
    return im

if __name__ == "__main__":
    image_generate("test.txt", "test.png", True)

