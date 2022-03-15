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
from sshtunnel import SSHTunnelForwarder

from AirbnbScrapySpider.items import AirbnbRoomItem, AirbnbRoomDetailItem, AirbnbRoomReviews, AirbnbLandlordDetailItem
from AirbnbScrapySpider.config import Config


class RoomsPipeline(object):
    def __init__(self):
        config = Config()
        with SSHTunnelForwarder(
                (config.server.ip, config.server.port),  # 指定ssh登录的跳转机的address，端口号
                ssh_username=config.server.username,  # 跳转机的用户名
                ssh_pkey=config.server.private_key_path,  # 私钥路径
                ssh_private_key_password=config.server.private_key_password,  # 跳转机的用户密码
                remote_bind_address=(config.mysql.host, config.mysql.port)) as server:  # mysql服务器的address，端口号
            # 建立数据库连接
            self.connection = pymysql.connect(host='127.0.0.1',  # 此处必须是是127.0.0.1
                                              port=server.local_bind_port,
                                              user=config.mysql.username,  # 数据库用户名
                                              passwd=config.mysql.password,  # 数据库密码
                                              db=config.mysql.database  # 数据库名称
                                              )

            # self.connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='airbnb', charset='utf8')
            # 创建操作游标
            self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        # 每种 item 都有 ID 属性，如果不具备这个属性，则此 item 出现了错误，直接返回
        adapter = ItemAdapter(item)
        if not adapter.get('ID'):
            return item

        # 如果是房屋的 item
        if isinstance(item, AirbnbRoomItem):
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
        # 如果是评论的 item
        elif isinstance(item, AirbnbRoomReviews):
            try:
                sql = "SELECT room_id FROM reviews WHERE review_id=%s"
                if self.cursor.execute(sql, adapter.get('ID')) == 1:
                    print("数据库已有记录")
                    return item
            except DropItem:
                print("操作数据库出现错误")
                raise DropItem(f"some wrong occurred when select from database")

            try:
                # 定义sql语句
                sql = "INSERT INTO airbnb.reviews (review_content, review_room_id, review_time, review_user_name) VALUES (%s, %s, %s, %s)"
                # 执行sql语句
                self.cursor.execute(sql, (str(adapter.get('review_content')),
                                          adapter.get('review_room_id'),
                                          adapter.get('review_time'),
                                          adapter.get('review_user_name')
                                          )
                                    )
                # 保存修改
                self.connection.commit()
            except DropItem:
                self.connection.rollback()
                print("changes have been rolled back")
                raise DropItem(f"some wrong occurred when insert to database")
            return item
        # 如果是房屋详情的 item
        elif isinstance(item, AirbnbRoomDetailItem):
            # 首先要存在这个房屋
            # 其次这个房屋的详情信息是不完整的（没有 room_price 信息）
            try:
                sql_is_exists = "SELECT room_price FROM rooms WHERE room_id=%s"
                if self.cursor.execute(sql_is_exists, adapter.get('ID')) == 1:
                    res = [item[0] for item in self.cursor.fetchall()]
                    if res.pop() is None:
                        print("数据库存在不完整的记录，可以完善")
                    else:
                        # 这里返回意思是，虽然数据库有这个房子，但是它的数据已经完整了
                        return item
                else:
                    # 这里返回意思是，数据库不存在这个房子，自然也不需要完善
                    return item
            except DropItem:
                print("操作数据库出现错误")
                raise DropItem(f"some wrong occurred when select from database")

            try:
                # 定义sql语句
                sql = "INSERT INTO airbnb.rooms (room_name, room_image_list, room_price, room_landlord_id, room_landlord_url, room_reviews_num, room_reviews_tag, room_position, room_description, room_metro, room_rule) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                # 执行sql语句
                self.cursor.execute(sql, (adapter.get('name'),
                                          adapter.get('img_list'),
                                          adapter.get('price'),
                                          adapter.get('landlord_id'),
                                          adapter.get('landlord_url'),
                                          adapter.get('reviews_num'),
                                          adapter.get('reviews_tag'),
                                          adapter.get('room_position'),
                                          adapter.get('description'),
                                          adapter.get('room_metro'),
                                          adapter.get('room_rule')
                                          )
                                    )
                # 保存修改
                self.connection.commit()
            except DropItem:
                self.connection.rollback()
                print("changes have been rolled back")
                raise DropItem(f"some wrong occurred when insert to database")
            return item
        # 如果是房东详情信息的 item
        elif isinstance(item, AirbnbLandlordDetailItem):
            try:
                sql = "SELECT room_landlord_id FROM landlords WHERE lanlord_id=%s"
                if self.cursor.execute(sql, adapter.get('ID')) == 1:
                    print("数据库已有记录")
                    return item
            except DropItem:
                print("操作数据库出现错误")
                raise DropItem(f"some wrong occurred when select from database")

            try:
                # 定义sql语句
                sql = "INSERT INTO landlords (lanlord_id, room_landlord_name, room_landlord_self_description, room_landlord_country, room_landlord_language, room_landlord_img) VALUES (%s, %s, %s, %s, %s)"
                # 执行sql语句
                self.cursor.execute(sql, (str(adapter.get('ID')),
                                          adapter.get('name'),
                                          adapter.get('description'),
                                          adapter.get('landlord_country'),
                                          adapter.get('landlord_language'),
                                          adapter.get('landlord_img')
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
