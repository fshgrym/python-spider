#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author:fsh
#time:'2017/12/15 22:54:19下午'
from scrapy.cmdline import execute

# import sys
# import os
#
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy','crawl','Dingdian'])