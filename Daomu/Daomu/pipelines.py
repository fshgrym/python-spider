# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class DaomuPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host="localhost",user="root",password="123456",db="article",port=3306,charset='utf8',use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = '''
        insert into daomu(title,create_time,crawl_time,category,text) values (%s,%s,%s,%s,%s)
        '''
        params =(item['title'],item['create_time'],item['crawl_time'],item['category'],item['text'])
        self.cursor.execute(insert_sql,params)
        self.conn.commit()
        return item

