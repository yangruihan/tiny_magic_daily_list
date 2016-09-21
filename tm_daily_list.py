#!/usr/bin/env python3
# -*-coding:utf-8-*-

"""Tiny Markdown Daily List

Usage:
    tm_daily_list.py (create | c)
    tm_daily_list.py (show | s) [-d <date>]
    tm_daily_list.py (complete | c) <index>
    tm_daily_list.py (redo | r) <index>
    tm_daily_list.py (remove | m) <index>
    tm_daily_list.py (delete | d) <date>
    tm_daily_list.py (-h | --help)
    tm_daily_list.py --version

Options:
    -h --help  Show the help document.
    --version  Show version.
    -d <date>  Modify daily list in some date

"""

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Tiny Markdown Daily List 1.0')
