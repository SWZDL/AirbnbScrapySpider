# there are many home list in database,
# but haven't their detail information,
# so this spider is to get their details.

import pymysql
import scrapy
from selenium import webdriver

from AirbnbScrapySpider.config import Config  # 导入配置文件

# 导入配置
config = Config()


class RoomDetailSpider(scrapy.Spider):
    name = 'roomDetailSpider'
    allowed_domains = ['airbnb.cn']
    start_urls = []

    def __init__(self, name=None, **kwargs):
        # 建立数据库连接
        self.index = 0
        connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='wenzengsheng', db='airbnb', charset='utf8')
        # 创建操作游标
        cursor = connection.cursor()
        sql = "SELECT room_url FROM rooms_list"
        cursor.execute(sql)
        res = cursor.fetchall()
        for url in res:
            self.start_urls.append(url[0])
        self.browser = config.getDriver()
        super().__init__(name, **kwargs)

    def start_requests(self):
        response = scrapy.Request(self.start_urls[self.index], callback=self.parse)
        yield response

    def parse(self, response, **kwargs):
        print(response.text)
        # parse the detail at here

        # continue to get the next one
        self.index += 1
        if self.index < len(self.start_urls):
            response = scrapy.Request(self.start_urls[self.index], callback=self.parse)
            yield response
        yield response
