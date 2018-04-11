#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author:fsh
#time:'2017/12/30 14:36:42下午'
# import socket
#
# print(socket.socket)
#
# print("Aftermonkey patch")
# from gevent import monkey
#
# monkey.patch_socket()
# print(socket.socket)
#
# import select
#
# print(select.select)
# monkey.patch_select()
# print("Aftermonkey patch")
# print(select.select)


'''多进程爬虫 | 多线程'''
from threading import Thread
from queue import Queue
import time
from lxml import etree
import requests


class DouBanSpider(Thread):
    def __init__(self,url,q):
        super(DouBanSpider, self).__init__()
        self.url = url
        self.q = q
        self.headers = {
            'Host': 'movie.douban.com',
            'Referer': 'https://movie.douban.com/top250?start=225&filter=',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36',
        }

    def run(self):
        self.parse_page()

    def send_request(self,url):
        '''
        用来发送网络请求
        :param url:
        :return: 返回网页源码
        '''
        i = 0
        while i<3:
            try:
                print('请求的url是%s'%url)
                return requests.get(url=url,headers=self.headers).text.encode('utf-8')
            except Exception as e:
                print('错误提示！！%s:%s'%(e,url))
                '''出现错误，请求三次后不再请求'''
                i += 1

    def parse_page(self):
        '''
               解析网站源码，并采用ｘｐａｔｈ提取　电影名称和平分放到队列中
               :return:
               '''
        response = self.send_request(self.url)
        html = etree.HTML(response)
        # 　获取到一页的电影数据
        node_list = html.xpath("//div[@class='info']")
        for move in node_list:
            # 电影名称
            title = move.xpath('.//a/span/text()')[0]
            # 评分
            score = move.xpath('//span[@class="rating_num"]/text()')[0]

            # 将每一部电影的名称跟评分加入到队列
            print(score,title)
            self.q.put(score+title)
def main():
    q = Queue()
    base_url =  'https://movie.douban.com/top250?start='
    #开始构造url
    url_list = [base_url+str(num) for num in range(0,255+1,25)]
    Process_list = []
    for url in url_list:
        p = DouBanSpider(url,q)
        p.start()
        time.sleep(5)
        Process_list.append(p)
    for i in Process_list:
        i.join()

    while not q.empty():
        print(q.get())
def douban():
    headers = {
        'Host': 'movie.douban.com',
        'Referer': 'https://movie.douban.com/top250?start=225&filter=',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36',
    }
    base_url = 'https://movie.douban.com/top250?start='
    # 开始构造url
    url_list = [base_url + str(num) for num in range(0, 255 + 1, 25)]
    for url in url_list:
        response = requests.get(url=url,headers=headers)
        html = etree.HTML(response.content)
        # 　获取到一页的电影数据
        node_list = html.xpath("//div[@class='info']")

        for move in node_list:
            # 电影名称
            title = move.xpath('.//a/span/text()')[0]
            # 评分
            score = move.xpath('//span[@class="rating_num"]/text()')[0]
            print(title,score)
if __name__ == '__main__':
    start = time.time()
    main()
    # douban()
    stop = time.time()
    print('耗时：%s'%(stop-start))
