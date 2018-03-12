# -*- coding: utf-8 -*-
from google_search.magic_google import MagicGoogle as GoogleSearch
from google_news.news import MagicGoogle_News as GoogleNews
from xueqiu import Xueqiu
new_kw = '创业板'

gs = GoogleSearch()
# data = gs.gain_data(query=new_kw, language='en', nums=100)

gn = GoogleNews()
data = gn.gain_data(query=new_kw, language='en', nums=100)

# mg = Xueqiu()
# infos = mg.gain_data(query='创业板 2018-03-11', nums=260)


def main():
    mg = Xueqiu.Xueqiu()
    infos = mg.gain_data(query='华通热力 2017 2016', nums=160)
    print(infos)


if __name__ == '__main__':
    main()
