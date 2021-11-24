# 清理 HTML 数据
# 验证爬取到的数据（检查项目是否包含某些字段）
# 检查重复（并丢弃它们）
# 将爬取到的项目存储在数据库中
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import pymysql


class HomesListPipeline(object):
    def __init__(self):
        # 建立数据库连接
        self.connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='wenzengsheng', db='airbnb', charset='utf8')
        # 创建操作游标
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        try:
            # 定义sql语句
            sql = "INSERT INTO airbnb.rooms_list VALUES (null,%s,%s,%s,%s,%s,%s,%s,%s)"

            # 执行sql语句
            self.cursor.execute(sql, (adapter.get('ID'),
                                      adapter.get('name'),
                                      adapter.get('img'),
                                      adapter.get('price'),
                                      adapter.get('score'),
                                      adapter.get('count'),
                                      adapter.get('shape'),
                                      adapter.get('number'))
                                )
            # 保存修改
            self.connection.commit()
        except:
            print("some wrong occurred when insert to database")
            self.connection.rollback()
            print("changes have been rolled back")
            raise DropItem(f"some wrong occurred when insert to database")
        return item

    def __del__(self):
        # 关闭操作游标
        self.cursor.close()
        # 关闭数据库连接
        self.connection.close()
