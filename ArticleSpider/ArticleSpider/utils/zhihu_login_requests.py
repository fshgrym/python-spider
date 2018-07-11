#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:fsh
import time
#time:'2017/12/17 22:41:13下午'
import os
import execjs
import requests
from PIL import Image
try:
    import http.cookiejar as cookielib
except:
    import cookielib
import re
session = requests.session()
#
session.cookies = cookielib.LWPCookieJar(filename='cookie.text')
try:
    session.cookies.load(ignore_discard=True)
except:
    print('cookie加载失败')
header = {
'Host':'www.zhihu.com',
'Origin':'https://www.zhihu.com',
'Pragma':'no-cache',
'Referer':'https://www.zhihu.com/',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.3 Safari/537.36',
'X-Requested-With':'XMLHttpRequest',
'X-Xsrftoken':'4171d4b4-862f-4c99-b16b-ac780cd3badd',
    }
def get_xsrf():
    response = session.get('https://www.zhihu.com',headers=header,verify=False).text
    match_obj = re.findall('.*name="_xsrf" value="(.*?)"',response)
    print(response)
    print(match_obj[0])
    return match_obj[0]

def get_index():
    response = session.get('https://www.zhihu.com',headers=header)
    with open('index_page.html','wb')as f:
        f.write(response.text.encode('utf-8'))
        print('ok')
def zhihu_login(account,password):
    if re.match('^1\d{10}',account):
        print('手机号码登录')
        post_url = 'https://www.zhihu.com/login/phone_num'
        get_captcha()
        captcha = input('验证码')
        post_data = {
            '_xsrf':get_xsrf(),
            'password':password,
            'phone_num':account,
            'captcha' :captcha
        }
    else:
        print('邮箱登录')
        post_url = 'https://www.zhihu.com/login/email'
        get_captcha()
        captcha = input('验证码')
        post_data = {
            '_xsrf': get_xsrf(),
            'password': password,
            'email': account,
            'captcha': captcha
        }
    response = session.post(post_url, post_data, headers=header, verify=False)
    session.cookies.save()

def get_captcha():
    t = str(int(time.time()*1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = requests.get(captcha_url, headers=header,verify=False)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
# 用pillow 的 Image 显示验证码
# 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
        captcha = input("please input the captcha\n>")

if __name__ == '__main__':
    zhihu_login('183127*33*1','****6*3*05*2')
    # get_index()
