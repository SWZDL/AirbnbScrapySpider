# 爬取房源列表
import json
import time

import scrapy
from AirbnbScrapySpider.config import Config  # 导入配置文件
# 导入配置
from AirbnbScrapySpider.items import AirbnbRoomItem

config = Config()


class HomesListSpider(scrapy.Spider):
    name = 'homesListSpider'
    allowed_domains = ['airbnb.cn']
    # 配置起始链接，根据城市地铁站开始
    start_urls = ['https://www.airbnb.cn/s/%E5%B9%BF%E5%B7%9E-%E9%92%9F%E5%B2%97/homes?refinement_paths%5B%5D=%2Fhomes&screen_size=large&map_toggle=false&checkin=2022-03-18&checkout=2022-03-19&adults=1']

    def __init__(self, **kwargs):
        self.pageNum = 1
        self.browser = config.getDriver()
        self.item = AirbnbRoomItem()
        super().__init__()

    def start_requests(self):
        response = scrapy.Request(self.start_urls[0], callback=self.parse, meta={"flag": "homes_list"})
        yield response

    def parse(self, response, **kwargs):
        for i in range(1, 21):  # 每页 20 个记录
            try:
                if response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/div[1]/div[1]/span/span/span/text()".format(i))[0].extract() == 'Plus':
                    print("=====去除 plus 房源，它的房源详情解析规则不一样======")
                    print(response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/div[1]/div[1]/span/span/span/text()".format(i))[0].extract())
                    print("=======================================================")
                    continue
                # self.item['name'] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/div[2]/div/div/text()".format(i))[0].extract()
                # img = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/a/div/img/@src".format(i)).extract_first()
                # if not img:
                #     img = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/a/div/img/@src".format(i)).extract_first()
                # self.item['img_list'] = img
                # self.item['price'] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[1]/div/span/span/span/span[1]/span[2]/text()".format(i))[0].extract()
                shape_and_count = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/div[1]/div/span/span/text()".format(i)).extract()
                self.item['shape'] = list(shape_and_count)[0]
                self.item['count'] = list(shape_and_count)[1]
                self.item['url'] = 'https://www.airbnb.cn' + response.xpath('/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/@href'.format(i)).extract_first()
                self.item['ID'] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/@href".format(i)).extract_first().split("?")[0].replace("/rooms/", "")
                print("shape:{}\tcount:{}\tid:{}\turl:{}\n".format(self.item['shape'], self.item['count'], self.item['ID'], self.item['url']))
                # 获取更加详细的房屋信息，如评论等
                # yield scrapy.Request(url=self.item['url'], callback=self.parse_room, meta={"flag": "room_detail"})
                yield self.item  # 将房屋信息存入数据库
                time.sleep(1)
            except Exception as e:
                print("=================================")
                print(e.args)
                self.browser.quit()
                print("=================================")
        self.pageNum += 1
        # 每个地点只爬 50 页，共 1000 个数据
        if self.pageNum <= 30:
            next_url = self.start_urls[0] + "&items_offset=" + str(20 * self.pageNum)
            if next_url:
                response = scrapy.Request(next_url, callback=self.parse, dont_filter=True, meta={"flag": "homes_list"})
                yield response
            else:
                self.browser.close()
        else:
            self.browser.close()

    # 对每个房东的信息进行访问解析
    def parse_landlord_detail(self, response):
        pass
        # item = response.meta["item"]  # 获取从response回调函数由meta传过来的 item 值
        # yield item

    def close(self, response):
        self.browser.close(self)
