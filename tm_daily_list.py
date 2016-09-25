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
    tm_daily_list.py (remove | m) <index> [-c]
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

FLAG_COMPLETED_MISSIONS = 1
FLAG_UNCOMPLETED_MISSIONS = 2


class TMDailyList:
    @staticmethod
    def new():
        """
        创建今日列表
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
        """
        if content.strip() == '':
            print(" Error: Content should not be Empty!")

        try:
            index, json_content, uncompleted_missions = TMDailyList.__validate_input_index(index, FLAG_UNCOMPLETED_MISSIONS)
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
        :param index: 任务索引号
        """
        try:
            index, json_content, uncompleted_missions = TMDailyList.__validate_input_index(index, FLAG_UNCOMPLETED_MISSIONS)
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
    def redo(index):
        """
        重做今日某个任务
        :param index: 任务索引号
        """
        try:
            index, json_content, completed_missions = TMDailyList.__validate_input_index(index, FLAG_COMPLETED_MISSIONS)
        except TMException:
            TMDailyList.show()
            return

        m = Mission()
        m.parse_from_json(completed_missions[index])
        del completed_missions[index]
        m.uncomplete()

        uncompleted_missions = json_content['content']['uncompleted']
        uncompleted_missions.append(m.get_json_str())

        TMDailyList.__write_json_to_file(json_content)
        TMDailyList.show()

    @staticmethod
    def remove(index, flag=None):
        """
        删除今日任务中的某个任务，默认删除未完成任务
        :param index: 任务索引号
        :param flag: 标记，如果 flag 不为 None，则删除已完成的某个任务
        """
        try:
            if flag: # 删除已完成的某个任务
                index, json_content, missions = TMDailyList.__validate_input_index(index, FLAG_COMPLETED_MISSIONS)
            else:
                index, json_content, missions = TMDailyList.__validate_input_index(index, FLAG_UNCOMPLETED_MISSIONS)
        except TMException:
            TMDailyList.show()
            return

        del missions[index]

        TMDailyList.__write_json_to_file(json_content)
        TMDailyList.show()

    @staticmethod
    def delete(date):
        """
        删除某日任务文件
        """
        try:
            TMDailyList.__delete_file(date)
        except TMException:
            return

        print('Delete file success!\n')

    @staticmethod
    def __validate_input_index(index, flag):
        """
        验证输入任务索引
        :param index: 任务索引
        :return: 索引-1， json 内容， 任务
        """
        try:
            index = int(index)
        except ValueError:
            print(" Error: Index should be Integer!\n")
            raise TMException("Index should be Integer")

        try:
            json_content = TMDailyList.__get_file_content_json()
        except TMException as e:
            raise e

        if flag == FLAG_COMPLETED_MISSIONS:
            missions = json_content["content"]["completed"]
        elif flag == FLAG_UNCOMPLETED_MISSIONS:
            missions = json_content["content"]["uncompleted"]

        if index > len(missions):
            print("Error: Index is out of range!\n")
            raise TMException("Index is out of range.")

        return index - 1, json_content, missions

    @staticmethod
    def __get_file_content_json(date=None):
        """
        从文件中获取 json 对象
        :param date: 日期
        :return: json 内容
        """
        file_date = time.strftime('%Y_%m_%d') if date is None else date
        file_name = DEFAULT_SAVE_PATH + file_date

        if not os.path.isfile(file_name):
            print('Error: There is no record at that date!\n')
            raise TMException('There is no record at that date')

        with open(file_name, 'r') as file:
            file_content = file.read()

        json_content = json.loads(file_content)

        return json_content

    @staticmethod
    def __delete_file(file_date):
        """
        将某一日期文件删除
        :param date: 日期
        """
        file_name = DEFAULT_SAVE_PATH + file_date

        if not os.path.isfile(file_name):
            print('Error: There is no file at that date!\n')
            raise TMException('There is no file at that date')

        try:
            os.remove(file_name)
        except OSError:
            print('Error: Delete file fail!\n')
            raise TMException('Delete file fail')

    @staticmethod
    def __write_json_to_file(json_content, date=None):
        """
        将 json 内容写入文件中
        :param json_content: json 内容
        :param date: 日期
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

    elif arguments['r'] or arguments['redo']:
        TMDailyList.redo(arguments['<index>'])

    elif arguments['m'] or arguments['remove']:
        if arguments['-c']:
            TMDailyList.remove(arguments['<index>'], True)
        else:
            TMDailyList.remove(arguments['<index>'])

    elif arguments['d'] or arguments['delete']:
        TMDailyList.delete(arguments['<date>'])
