#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author:fsh
#time:'2018/1/6 0:12:56上午'
import requests
import time
import random
import hashlib
import json


# o = n.md5("fanyideskweb" + t + i + "aNPG!!u6sesA>hBAW1@(-");

class YouDao:
    def __init__(self):
        '''有道翻译检测cookie'''
        self.url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
        self.headers = headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie':'OUTFOX_SEARCH_USER_ID_NCOO=1608743378.8606813; OUTFOX_SEARCH_USER_ID=-893206781@119.145.82.50; _ntes_nnid=eeee572b5f45926956875f3d7fc39de5,1511442238312; _ga=GA1.2.448173872.1511439058; _gid=GA1.2.1162310313.1515085561; JSESSIONID=aaa0H9_0_nTnGcpLhlhdw; fanyi-ad-id=39535; fanyi-ad-closed=1; ___rl__test__cookies=1515170086265',
            'Host': 'fanyi.youdao.com',
            'Origin': 'http://fanyi.youdao.com',
            'Referer': 'http://fanyi.youdao.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.3 Safari/537.36'
        }
        self.salt = salt = int(time.time() * 1000 + random.randint(0, 10))
    def parse(self):
        while True:
            content = input('请输入你要翻译的内容(输入q退出)：')
            t = content
            if t =='q':
                break
            i = str(self.salt)  # int不能用于相加
            o = hashlib.md5(("fanyideskweb" + t + i + "aNPG!!u6sesA>hBAW1@(-").encode('utf-8')).hexdigest()

            data = {
                'i': content,
                'from': 'AUTO',
                'to': 'AUTO',
                'smartresult': 'dict',
                'client': 'fanyideskweb',
                'salt': self.salt,
                'sign': o,
                'doctype': 'json',
                'version': '2.1',
                'keyfrom': 'fanyi.web',
                'action': 'FY_BY_REALTIME',
                'typoResult': 'false'
            }
            response = requests.post(self.url, data=data, headers=self.headers).text
            target = json.loads(response)
            if target['errorCode']==50:
                print('翻译失败了')
            else:
                print('翻译的结果是：%s'%target['translateResult'][0][0]['tgt'])

if __name__ == '__main__':
    fanyi = YouDao()
    fanyi.parse()