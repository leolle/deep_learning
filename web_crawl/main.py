# -*- coding: utf-8 -*-

import MagicGoogle
from MagicGoogle import MagicGoogle
from Xueqiu.Xueqiu import Xueqiu
new_kw = '李小璐'

# mg = MagicGoogle()
# data = mg.gain_data(query=new_kw, language='en', nums=100)

mg = Xueqiu()
infos = mg.gain_data(query='创业板 2018-03-11', nums=260)


def main():
    mg = Xueqiu.Xueqiu()
    infos = mg.gain_data(query='华通热力 2017 2016', nums=160)
    print(infos)


if __name__ == '__main__':
    main()
