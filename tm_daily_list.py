#!/usr/bin/env python3
# -*-coding:utf-8-*-

"""Tiny Markdown Daily List

Usage:
    tm_daily_list.py (new | n)
    tm_daily_list.py (show | s) [-d <date>]
    tm_daily_list.py (add | a) <content> [-p <priority>]
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

from tm_daily_exception import TMException
from tm_daily_list_mission import Mission

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
    def new():
        """
        创建今日列表
        :return:
        """
        file_date = time.strftime('%Y_%m_%d')
        file_name = DEFAULT_SAVE_PATH + file_date

        if os.path.isfile(file_name):
            print("Today's daily list has already created!")
        else:
            TMDailyList.__write_json_to_file(DEFAULT_JSON_CONTENT.format(file_date))

            print("Today's daily list has been created!")
            print("Press 'A' to add content, other keys exit!")
            user_input_key = input('> ')

            if user_input_key != 'a' and user_input_key != 'A':
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

        json_content = TMDailyList.__get_file_content_json(date)
        if not json_content:
            return

        # 按格式输出
        print('──────────%s──────────' % file_date)

        # 输出未完成任务
        print('► Uncompleted:')
        for idx, m in enumerate(json_content['content']['uncompleted']):
            mission = Mission()
            mission.parse_from_json(m)
            print("  □ %d. " % (idx + 1) + mission.content)

        # 输出已完成任务
        print('► Completed:')
        for idx, m in enumerate(json_content['content']['completed']):
            mission = Mission()
            mission.parse_from_json(m)
            print("  ■ %d. " % (idx + 1) + mission.content)

        print("──────────────────────────────")

    @staticmethod
    def add(content=None, priority=None):
        """
        向今日列表中添加内容
        :return:
        """
        json_content = TMDailyList.__get_file_content_json()
        if not json_content:
            return

        if not content:
            print('Please input mission content (content [priority]): ')
            input_content = input('> ')
            if len(input_content) == 2:
                content, priority = input_content
            else:
                content = input_content

        m = Mission(content)

        if not priority:
            json_content['content']['uncompleted'].append(m.get_json_str())
        else:
            json_content['content']['uncompleted'].insert(priority - 1, m.get_json_str())

        TMDailyList.__write_json_to_file(json_content)
        TMDailyList.show()

    @staticmethod
    def modify(index, content):
        """
        修改某一任务内容
        :param index: 任务索引
        :param content: 修改后内容
        :return:
        """
        if content.strip() == '':
            print(" Error: Content should not be Empty!")

        try:
            index, json_content, uncompleted_missions = TMDailyList.__validate_input_index(index)
        except TMException:
            TMDailyList.show()
            return

        uncompleted_missions[index]['content'] = content
        TMDailyList.__write_json_to_file(json_content)
        TMDailyList.show()

    @staticmethod
    def complete(index):
        """
        完成今日某个任务
        :param index:
        :return:
        """
        try:
            index, json_content, uncompleted_missions = TMDailyList.__validate_input_index(index)
        except TMException:
            TMDailyList.show()
            return

        m = Mission()
        m.parse_from_json(uncompleted_missions[index])
        del uncompleted_missions[index]
        m.complete()

        completed_missions = json_content['content']['completed']
        completed_missions.append(m.get_json_str())

        TMDailyList.__write_json_to_file(json_content)
        TMDailyList.show()

    @staticmethod
    def __validate_input_index(index):
        """
        验证输入任务索引
        :param index:
        :return:
        """
        try:
            index = int(index)
        except ValueError:
            print(" Error: Index should be Integer")
            raise TMException("index should be Integer")

        json_content = TMDailyList.__get_file_content_json()
        if not json_content:
            raise TMException("Get content json from file error.")

        uncompleted_missions = json_content["content"]["uncompleted"]
        if index > len(uncompleted_missions):
            print("Error: Index is out of range!")
            raise TMException("Index is out of range.")

        return index - 1, json_content, uncompleted_missions

    @staticmethod
    def __get_file_content_json(date=None):
        """
        从文件中获取 json 对象
        :param date:
        :return:
        """
        file_date = time.strftime('%Y_%m_%d') if date is None else date
        file_name = DEFAULT_SAVE_PATH + file_date

        if not os.path.isfile(file_name):
            print('Error: There is no record at that date!')
            return None

        with open(file_name, 'r') as file:
            file_content = file.read()

        json_content = json.loads(file_content)

        return json_content

    @staticmethod
    def __write_json_to_file(json_content, date=None):
        """
        将 json 内容写入文件中
        :param json_content: json 内容
        :param date: 日期
        :return:
        """
        file_date = time.strftime('%Y_%m_%d') if date is None else date
        file_name = DEFAULT_SAVE_PATH + file_date
        json_content = json_content if isinstance(json_content, str) else json.dumps(json_content, indent=2)

        with open(file_name, 'w') as file:
            file.write(json_content)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    # 创建 data 文件夹
    if not os.path.exists(DEFAULT_SAVE_PATH):
        os.mkdir(DEFAULT_SAVE_PATH)

    if arguments['n'] or arguments['new']:
        TMDailyList.new()

    elif arguments['s'] or arguments['show']:
        if not arguments['-d']:
            TMDailyList.show()
        else:
            pattern = re.compile(r"^\d{4}_\d{2}_\d{2}$")
            if not pattern.match(arguments['-d']):
                print("Input date should like this: 2016_09_23")
            else:
                TMDailyList.show(arguments['-d'])

    elif arguments['a'] or arguments['add']:
        if not arguments['-p']:
            TMDailyList.add(arguments['<content>'])
        else:
            TMDailyList.add(arguments['<content>'], arguments['-p'])

    elif arguments['c'] or arguments['complete']:
        TMDailyList.complete(arguments['<index>'])

    elif arguments['f'] or arguments['modify']:
        TMDailyList.modify(arguments['<index>'], arguments['<content>'])
