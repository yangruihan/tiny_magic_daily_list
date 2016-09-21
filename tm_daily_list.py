#!/usr/bin/env python3
# -*-coding:utf-8-*-

"""Tiny Markdown Daily List

Usage:
    tm_daily_list.py (new | n)
    tm_daily_list.py (show | s) [-d <date>]
    tm_daily_list.py (complete | c) <index>
    tm_daily_list.py (redo | r) <index>
    tm_daily_list.py (add | a) [<index>] <content>
    tm_daily_list.py (remove | m) <index>
    tm_daily_list.py (delete | d) <date>
    tm_daily_list.py (-h | --help)
    tm_daily_list.py --version


Options:
    -h --help  Show the help document.
    --version  Show version.
    -d <date>  Modify daily list in some date

"""

import os
import time

from docopt import docopt

DEFAULT_SAVE_PATH = "./data/"


class TMDailyList:
    @staticmethod
    def create():
        """
        创建今日列表
        :return:
        """
        file_name = DEFAULT_SAVE_PATH + time.strftime("%Y_%m_%d_list.md")

        if os.path.isfile(file_name):
            print("Today's daily list has already created!")
        else:
            open(file_name, 'a').close()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')
    print(arguments)

    # 创建 data 文件夹
    if not os.path.exists(DEFAULT_SAVE_PATH):
        os.mkdir(DEFAULT_SAVE_PATH)

    if arguments['n'] or arguments['new']:
        TMDailyList.create()
