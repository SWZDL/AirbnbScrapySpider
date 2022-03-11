# 清理 HTML 数据
# 验证爬取到的数据（检查项目是否包含某些字段）
# 检查重复（并丢弃它们）
# 将爬取到的项目存储在数据库中
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import pymysql
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from AirbnbScrapySpider.items import AirbnbRoomItem


class RoomsPipeline(object):
    def __init__(self):
        # 建立数据库连接
        self.connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='airbnb', charset='utf8')
        # 创建操作游标
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        print("是否与目标一致：{}".format(isinstance(item, AirbnbRoomItem)))
        if isinstance(item, AirbnbRoomItem):
            adapter = ItemAdapter(item)
            if not adapter.get('ID'):
                return item
            try:
                sql = "SELECT room_id FROM rooms WHERE room_id=%s"
                if self.cursor.execute(sql, adapter.get('ID')) == 1:
                    print("数据库已有记录")
                    return item
            except DropItem:
                print("操作数据库出现错误")
                raise DropItem(f"some wrong occurred when select from database")

            try:
                # 定义sql语句
                sql = "INSERT INTO airbnb.rooms (room_id, room_count, room_shape, room_url) VALUES (%s, %s, %s, %s)"
                # 执行sql语句
                self.cursor.execute(sql, (str(adapter.get('ID')),
                                          # adapter.get('name'),
                                          # adapter.get('img_list'),
                                          # adapter.get('price'),
                                          adapter.get('count'),
                                          adapter.get('shape'),
                                          adapter.get('url')
                                          # adapter.get('landlord_id'),
                                          # adapter.get('landlord_url'),
                                          # adapter.get('reviews_num'),
                                          # adapter.get('reviews_tag'),
                                          # adapter.get('room_position'),
                                          # adapter.get('description'),
                                          # adapter.get('room_metro'),
                                          # adapter.get('room_rule')
                                          )
                                    )
                # 保存修改
                self.connection.commit()
            except DropItem:
                self.connection.rollback()
                print("changes have been rolled back")
                raise DropItem(f"some wrong occurred when insert to database")
            return item

    def __del__(self):
        # 关闭操作游标
        self.cursor.close()
        # 关闭数据库连接
        self.connection.close()
