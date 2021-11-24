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


class HomesListPipeline(object):
    def __init__(self):
        # 建立数据库连接
        self.connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='wenzengsheng', db='airbnb', charset='utf8')
        # 创建操作游标
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if not adapter.get('ID'):
            return item
        try:
            sql = "SELECT room_id FROM rooms_list WHERE room_id=%s"
            if self.cursor.execute(sql, adapter.get('ID')) == 1:
                return item
        except DropItem:
            raise DropItem(f"some wrong occurred when select from database")

        try:
            # 定义sql语句
            sql = "INSERT INTO airbnb.rooms_list (room_id, room_name, room_img, room_price, room_count, room_shape, room_url) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            # 执行sql语句
            self.cursor.execute(sql, (adapter.get('ID'),
                                      adapter.get('name'),
                                      adapter.get('img'),
                                      adapter.get('price'),
                                      adapter.get('count'),
                                      adapter.get('shape'),
                                      adapter.get('url')
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
