# -*- coding: utf-8 -*-
import regex as re

def format_punctuations(s):
    return s.replace('「', '“') \
            .replace('」', '”') \
            .replace('『', '“') \
            .replace('』', '”')

non_punct = r'[^\n\p{P}0-9a-zA-Z]' # \p{P} for punctuations
num_or_en = r'[0-9][0-9.]*%?|[a-zA-Z]+'
pre_space_pat = re.compile(r'(?<={}) *({})'.format(non_punct, num_or_en))
aft_space_pat = re.compile(r'({}) *(?={})'.format(num_or_en, non_punct))

def format_numbers(s):
    s1 = pre_space_pat.sub(r' \1', s)
    s2 = aft_space_pat.sub(r'\1 ', s1)
    return s2

if __name__ == '__main__':
    import sys
    print(format_numbers(format_punctuations(sys.stdin.read())))
