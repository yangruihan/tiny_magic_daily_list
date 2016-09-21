#!/usr/bin/env python3
# -*-coding:utf-8-*-

"""Tiny Markdown Daily List

Usage:
    tm_daily_list.py (new | n)
    tm_daily_list.py (show | s) [-d <date>]
    tm_daily_list.py (add | a) [<index>] <content>
    tm_daily_list.py (modify | f) <index> <content>
    tm_daily_list.py (complete | c) <index>
    tm_daily_list.py (redo | r) <index>
    tm_daily_list.py (remove | m) <index>
    tm_daily_list.py (delete | d) <date>
    tm_daily_list.py (-h | --help)
    tm_daily_list.py --version


Options:
    -h --help  Show the help document.
    --version  Show version.
    -d <date>  Modify daily list in some date, e.g. show -d 2016_09_23

"""

import json
import os
import re
import time

from docopt import docopt

DEFAULT_SAVE_PATH = "./data/"
DEFAULT_JSON_CONTENT = r"""{{
    "title": "",
    "time": "{0}",
    "content":
    {{
        "completed":[],
        "uncompleted":[]
    }}
}}
"""


class TMDailyList:
    @staticmethod
    def create():
        """
        创建今日列表
        :return:
        """
        file_date = time.strftime('%Y_%m_%d')
        file_name = DEFAULT_SAVE_PATH + file_date

        if os.path.isfile(file_name):
            print("Today's daily list has already created!")
        else:
            with open(file_name, 'a') as file:
                file.write(DEFAULT_JSON_CONTENT.format(file_date))

            print("Today's daily list has been created!")
            print("Press 'A' to add content, other keys exit!")
            user_input_key = input('> ')

            if user_input_key != 'a' or user_input_key != 'A':
                return
            else:
                # 调用添加方法
                TMDailyList.add()

    @staticmethod
    def show(date=None):
        """
        显示今日列表内容
        :return:
        """
        file_date = time.strftime('%Y_%m_%d') if date is None else date
        file_name = DEFAULT_SAVE_PATH + file_date

        if not os.path.isfile(file_name):
            print('Error: There is no record at that date!')
            return

        with open(file_name, 'r') as file:
            file_content = file.read()

        json_content = json.loads(file_content)

        # 按格式输出
        print('──────────%s──────────' % file_date)

        # 输出未完成任务
        print('► Uncompleted:')
        for i in json_content['content']['uncompleted']:
            print("  □ " + i)

        # 输出已完成任务
        print('► Completed:')
        for i in json_content['content']['uncompleted']:
            print("  ■ " + i)

        print("──────────────────────────────")

    @staticmethod
    def add():
        """
        向今日列表中添加内容
        :return:
        """
        pass


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    # 创建 data 文件夹
    if not os.path.exists(DEFAULT_SAVE_PATH):
        os.mkdir(DEFAULT_SAVE_PATH)

    if arguments['n'] or arguments['new']:
        TMDailyList.create()

    if arguments['s'] or arguments['show']:
        if not arguments['-d']:
            TMDailyList.show()
        else:
            pattern = re.compile(r'^\d{4}_\d{2}_\d{2}$')
            if not pattern.match(arguments['-d']):
                print("Input date should like this: 2016_09_23")
