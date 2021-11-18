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
        try:
            # 定义sql语句
            sql = "INSERT INTO airbnb.rooms_list (`rooms_list_id`,`room_id`,`room_name`,`room_img`,`room_price`,`room_score`,`room_count`,`room_shape`,`room_number`, VALUES ('',%s,%s,%s,%s,%s,%s,%s,%s)"

            # 执行sql语句
            self.cursor.execute(sql, (item['ID'], item['name'], item['img'], item['price'], item['score'], item['count'], item['shape'], item['number']))
            # 保存修改
            self.connection.commit()
        except:
            print("something wrong")
            self.connection.rollback()
        return item

    def __del__(self):
        # 关闭操作游标
        self.cursor.close()
        # 关闭数据库连接
        self.connection.close()


class AirbnbscrapyspiderPipeline:
    vat_factor = 1.15

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('price'):
            if adapter.get('price_excludes_vat'):
                adapter['price'] = adapter['price'] * self.vat_factor
            return item
        else:
            raise DropItem(f"Missing price in {item}")
