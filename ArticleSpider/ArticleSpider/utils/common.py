#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author:fsh
#time:'2017/12/16 16:25:08下午'
import hashlib
import re

def get_md5(url):
    if isinstance(url,str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(text):
    '''从字符串中提取数字'''
    nums_re = re.match(".*?(\d+).*", text)
    if nums_re:
        value = int(nums_re.group(1))
    else:
        value = 0
    return value

if __name__ == '__main__':
    print(get_md5('http://jobbole.com'))