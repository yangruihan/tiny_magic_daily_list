#!/usr/bin/env python3
# -*-coding:utf-8-*-

import time


class Mission:
    """
    任务类:
        用于记录每一条任务的详细信息
    """

    def __init__(self, content=None):
        if content is not None:
            self.content = content  # 记录任务内容
            self.create_time = time.strftime("%Y/%m/%d %H:%M:%S")  # 记录创建时间
            self.last_modify_time = time.strftime("%Y/%m/%d %H:%M:%S")  # 最后一次修改时间
            self.complete_time = ""  # 任务完成时间
        else:
            self.content = ""
            self.create_time = ""
            self.last_modify_time = ""
            self.complete_time = ""

    def complete(self):
        self.last_modify_time = time.strftime("%Y/%m/%d %H:%M:%S")
        self.complete_time = time.strftime("%Y/%m/%d %H:%M:%S")

    def uncomplete(self):
        self.last_modify_time = time.strftime("%Y/%m/%d %H:%M:%S")
        self.complete_time = ""

    def get_json_str(self):
        """
        得到 json 字符串
        :return: json 字符串
        """
        return self.__dict__

    def parse_from_json(self, json):
        """
        从 json 字典解析属性
        :param json: json 字典
        """
        if 'content' in json:
            self.content = json['content']

        if 'create_time' in json:
            self.create_time = json['create_time']

        if 'last_modify_time' in json:
            self.last_modify_time = json['last_modify_time']

        if 'complete_time' in json:
            self.complete_time = json['complete_time']
