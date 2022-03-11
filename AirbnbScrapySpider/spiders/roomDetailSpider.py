# there are many home list in database,
# but haven't their detail information,
# so this spider is to get their details.

import pymysql
import scrapy
from sshtunnel import SSHTunnelForwarder

from AirbnbScrapySpider.config import Config  # 导入配置文件

# 导入配置
config = Config()


class RoomDetailSpider(scrapy.Spider):
    name = 'roomDetailSpider'
    allowed_domains = ['airbnb.cn']
    start_urls = []

    def __init__(self, name=None, **kwargs):
        self.browser = config.getDriver()
        self.url_list = self.get_room_url()
        self.start_urls = [self.url_list.pop()]
        super().__init__(name, **kwargs)

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
                                         port=config.mysql.port,
                                         user=config.mysql.username,  # 数据库用户名
                                         passwd=config.mysql.password,  # 数据库密码
                                         db=config.mysql.database  # 数据库名称
                                         )

            # self.connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='airbnb', charset='utf8')
            # 创建操作游标
            cursor = connection.cursor()
            sql = "SELECT room_url FROM rooms where rooms.room_reviews_num is null limit 100"
            cursor.execute(sql)
            res = cursor.fetchall()
            return list(res)

    def start_requests(self):
        response = scrapy.Request(self.start_urls[0], callback=self.parse, meta={"flag": "room_detail"})
        yield response

    def parse(self, response, **kwargs):
        # parse the detail at here
        reviews_count = response.xpath("/html/body/div[3]/div/main/div[2]/div/div/div/div[2]/div/div[1]/div/main/div[4]/div/div/div/section/div[2]/div[1]/div/div/div/div/div/span/text()").extract()
        if reviews_count:  # 如果有评论就采集，否则跳过
            price = response.xpath("/html/body/div[3]/div/main/div/div/div/div/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/div/div/div/div/div/div[1]/div[1]/div/span[2]/span/text()").extract()
            description = response.xpath("/html/body/div[8]/div/div/div/div/div/div/section/div/section/div/div[1]/div[2]")
            img_list_div = response.xpath('/html/body/div[3]/div/main/div/div/div/div/div[1]/div[1]/div/div/div[1]/div/div[1]')
            print("price:{}\ndescription:{}\nimg_list_div:{}".format(price, description, img_list_div))
            # yield self.item  # 将房屋信息存入数据库
            # yield scrapy.Request(url=landlord_detail_url, callback=self.parse_landlord_detail, meta={"item": item})  # 通过 参数meta 可以将item参数传递进 callback回调函数,再由 response.meta[...]取出来
        # continue to get the next one
        if len(self.url_list) >= 1:
            response = scrapy.Request(self.url_list.pop(), callback=self.parse, meta={"flag": "room_detail"})
            yield response
        else:
            self.browser.close()
