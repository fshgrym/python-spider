#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author:fsh
#time:'2017/12/23 13:58:26下午'
import requests
import MySQLdb
from scrapy.selector import Selector
conn = MySQLdb.connect(host="localhost",user="root",password="123456",db="article",port=3306,charset='utf8',use_unicode=True)
cursor = conn.cursor()
def crawl_ips():
    '''爬取西刺免费ip'''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    }
    for i in range(1568):
        print('正在爬取第%s'%i)
        url = 'http://www.xicidaili.com/nn/{}'.format(i)
        re = requests.get(url,headers=headers)
        selector = Selector(text=re.text)
        all_trs = selector.css('#ip_list tr')
        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css('.bar::attr(title)').extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])
            all_texts = tr.css('td::text').extract()
            ip = all_texts[0]
            port = all_texts[1]
            proxy_type = all_texts[5]
            ip_list.append([ip,port,speed,proxy_type])
        for ip_info in ip_list:
            cursor.execute(
                '''INSERT INTO proxy_ip(ip,port,speed,proxy_type) VALUES('{0}','{1}',{2},'{3}') ON DUPLICATE KEY UPDATE speed=VALUES(speed)'''.format(ip_info[0],ip_info[1],ip_info[2],ip_info[3]))
            conn.commit()
class GetIp(object):
    def delete_ip(self,ip):
        delete_sql = '''
        delete from proxy_ip where ip='{0}'
        '''.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True
    def judge_ip(self,ip,port,proxy_type):
        http_url = 'http://www.baidu.com'
        proxy_url = '{0}://{1}:{2}'.format(proxy_type,ip,port)
        http=proxy_type
        try:
            poxy_dict ={
                http:proxy_url,
            }
            response = requests.get(http_url,proxies=poxy_dict)
            return True
        except Exception as e:
            print('invalid ip and port')
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >=200 and code<300:
                print('effective ip')
                return True
            else:
                print('invalid')
                self.delete_ip(ip)
                return False


    def get_random(self):
        '''随机取ip'''
        random_sql = '''
        select ip,port,proxy_type from proxy_ip ORDER BY RAND() LIMIT 1 
        '''
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            proxy_type = ip_info[2]
            judge_re = self.judge_ip(ip,port,proxy_type)
            if judge_re:
                ip = '{0}://{1}:{2}'.format(proxy_type,ip,port)
                return ip
            else:
                return self.get_random()

    # crawl_ips()

