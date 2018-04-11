# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
import codecs
import json
import MySQLdb
import MySQLdb.cursors


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):
    def __init__(self):
        # self.conn = MySQLdb.connect('host','user','password','db_name',charset='utf8')
        # self.conn = MySQLdb.connect(host='127.0.0.1', user='root', password='123456', db='article', charset='utf8',use_unicode=True,port=3306)
        self.conn = MySQLdb.connect(host="localhost",user="root",password="123456",db="article",port=3306,charset='utf8',use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql ='''
        insert into article_spider(title,create_data,url,url_object_id,front_image_url,front_image_path,praise_nums,comment_nums,fav_nums,tags,content) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        self.cursor.execute(insert_sql,(item['title'],item['create_data'],item['url'],item['url_object_id'],item['front_image_url'],item['front_image_path'],item['praise_nums'],item['comment_nums'],item['fav_nums'],item['tags'],item['content']))
        self.conn.commit()
        return item


class MysqlTwistedPipline(object):
    '''使用scrapy自带的异步来存储数据，因为当爬虫的速度过快，会堵塞'''

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):

        dbparms=dict(
        host = settings['MYSQL_HOST'],
        user = settings['MYSQL_USER'],
        password = settings['MYSQL_PASSWORD'],
        db=settings['MYSQL_DBNAME'],
        charset = 'utf8',
        cursorclass = MySQLdb.cursors.DictCursor,
        use_unicode=True
        )
        # 使用异步api
        dbpool=adbapi.ConnectionPool('MySQLdb',**dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        '''使用twisted使用mysql插入异步执行'''
        query = self.dbpool.runInteraction(self.db_insert,item)
        query.addErrback(self.handle_error,item,spider)

    def handle_error(self,failure,item,spider):
        '''处理异常'''
        print(failure)

    def db_insert(self,cursor,item):
        # 具体的插入
        '''根据不同的item,构建不同pipelines'''
        # if item.__class__.__name__ == 'JobBoleArticleItem':
        # insert_sql = '''
        # insert into article_spider(title,create_data,url,url_object_id,front_image_url,front_image_path,praise_nums,comment_nums,fav_nums,tags,content) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        # cursor.execute(insert_sql, (item['title'], item['create_data'], item['url'], item['url_object_id'], item['front_image_url'],
        # item['front_image_path'], item['praise_nums'], item['comment_nums'], item['fav_nums'], item['tags'],
        # item['content']))
        insert_sql,params = item.get_insert_sql()
        cursor.execute(insert_sql,params)


class JsonWithEncodingPipeline(object):

    '''自定义存储json'''

    def __init__(self):
        self.file = codecs.open('article.json','w',encoding='utf-8')

    def process_item(self,item,spider):
        lines = json.dumps(dict(item),ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item

    def spider_closed(self,spidre):
        self.file.close()


class JsonItemExporterPipeline(object):
    '''调用scrapy提供的JsonItemExporter来保存json'''
    def __init__(self):
        self.file = open('articleexport.json','wb')
        self.exporter = JsonItemExporter(self.file,encoding='utf-8',ensure_ascii=False)
        self.exporter.start_exporting()

    def colse_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class ArticleImagePipeline(ImagesPipeline):
    '''#自定义pipelines,用来处理图片'''
    def item_completed(self, results, item, info):
        if 'front_image_url' in item:

            for ok,value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item
