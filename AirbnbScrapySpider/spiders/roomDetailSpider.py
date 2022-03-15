# there are many home list in database,
# but haven't their detail information,
# so this spider is to get their details.

import pymysql
import scrapy
from sshtunnel import SSHTunnelForwarder

from AirbnbScrapySpider.config import Config  # 导入配置文件

# 导入配置
from AirbnbScrapySpider.items import AirbnbRoomDetailItem

config = Config()


class RoomDetailSpider(scrapy.Spider):
    name = 'roomDetailSpider'
    allowed_domains = ['airbnb.cn']
    start_urls = []

    def get_room_url(self):
        # 建立数据库连接
        with SSHTunnelForwarder(
                (config.server.ip, config.server.port),  # 指定ssh登录的跳转机的address，端口号
                ssh_username=config.server.username,  # 跳转机的用户名
                ssh_pkey=config.server.private_key_path,  # 私钥路径
                ssh_private_key_password=config.server.private_key_password,  # 跳转机的用户密码
                remote_bind_address=(config.mysql.host, config.mysql.port)) as server:  # mysql服务器的address，端口号
            # 建立数据库连接
            connection = pymysql.connect(host='127.0.0.1',  # 此处必须是是127.0.0.1
                                         port=server.local_bind_port,
                                         user=config.mysql.username,  # 数据库用户名
                                         passwd=config.mysql.password,  # 数据库密码
                                         db=config.mysql.database  # 数据库名称
                                         )
            # 创建操作游标
            cursor = connection.cursor()
            sql = "SELECT room_url FROM rooms where rooms.room_name is null limit 100 offset 400"
            cursor.execute(sql)
            res = [item[0] for item in cursor.fetchall()]
            return res

    def __init__(self, name=None, **kwargs):
        self.browser = config.getDriver()
        self.url_list = self.get_room_url()
        self.start_urls = [self.url_list.pop()]
        super().__init__(name, **kwargs)

    def start_requests(self):
        response = scrapy.Request(self.start_urls[0], callback=self.parse, meta={"flag": "room_detail"})
        yield response

    def parse(self, response, **kwargs):
        # parse the detail at here
        reviews_num = response.xpath("/html/body/div[3]/div/main/div/div/div/div/div[2]/div/div[1]/div/div[4]/div/div/div/section/div[2]/div[1]/div/div/div/div/div/span/text()").extract_first()
        print("=================parse room detail============================")
        print("reviews_num：{}".format(reviews_num))
        print("=============================================")
        if reviews_num:
            airbnb_room_detail_item = AirbnbRoomDetailItem()
            airbnb_room_detail_item['ID'] = response.url.split("?")[0].split('/')[-1]
            airbnb_room_detail_item['name'] = response.xpath("/html/body/div[3]/div/main/div/div/div/div/div[2]/div/div[1]/div/div[1]/div/div/div/section/div[1]/div[2]/div/h1/div/text()").extract_first()
            airbnb_room_detail_item['price'] = response.xpath("/html/body/div[3]/div/main/div/div/div/div/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/div/div/div/div/div/div/div[1]/div/span[2]/span/text()").extract_first()
            airbnb_room_detail_item['landlord_url'] = "https://www.airbnb.cn{}".format(response.xpath("/html/body/div[3]/div/main/div/div/div/div/div[2]/div/div[1]/div/div[9]/div/div/div/section/div[1]/div/div/div[2]/div/div/div/a/@href").extract_first())
            airbnb_room_detail_item['landlord_id'] = airbnb_room_detail_item['landlord_url'].split("/")[-1]
            airbnb_room_detail_item['reviews_tag'] = response.xpath("/html/body/div[3]/div/main/div/div/div/div/div[2]/div/div[1]/div/div[4]/div/div/div/section/div[2]/div[4]//span/text()").extract()
            airbnb_room_detail_item['reviews_num'] = reviews_num
            print("=============================================")
            print("name:{}\nprice:{}\nlandlord_url:{}\nlandlord_id:{}\nreviews_tag:{}\nreviews_num:{}".format(airbnb_room_detail_item['name'], airbnb_room_detail_item['price'], airbnb_room_detail_item['landlord_url'], airbnb_room_detail_item['landlord_id'], airbnb_room_detail_item['reviews_tag'], airbnb_room_detail_item['reviews_num']))
            print("=============================================")
            yield airbnb_room_detail_item  # 将房屋信息存入数据库
            if len(self.url_list) > 0:
                response = scrapy.Request(self.url_list.pop(), callback=self.parse, dont_filter=True, meta={"flag": "room_detail"})
                yield response
