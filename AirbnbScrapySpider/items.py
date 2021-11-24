# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AirbnbHomeListItem(scrapy.Item):
    # define the fields for your item here like:
    # 房源ID
    ID = scrapy.Field()
    # 房源名称
    name = scrapy.Field()
    # 房源图片列表
    img = scrapy.Field()
    # 房源价格
    price = scrapy.Field()
    # 类型
    shape = scrapy.Field()
    # 房间数量
    count = scrapy.Field()
    # 房源详情url
    url = scrapy.Field()
