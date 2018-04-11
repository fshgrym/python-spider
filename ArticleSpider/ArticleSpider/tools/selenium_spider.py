#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author:fsh
#time:'2017/12/23 21:25:48下午'
from selenium import webdriver
browser = webdriver.Chrome()
browser.get('http://www.baidu.com')
print(browser.page_source)
browser.quit()