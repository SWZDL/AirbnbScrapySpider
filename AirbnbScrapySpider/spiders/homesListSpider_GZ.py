# 爬取房源列表
import json

import scrapy

from AirbnbScrapySpider.config import Config  # 导入配置文件

# 导入配置
config = Config()


class HomesListSpider(scrapy.Spider):
    name = 'homesListSpiderGZ'
    allowed_domains = ['airbnb.cn']
    start_urls = ['https://www.airbnb.cn/s/%E5%B9%BF%E5%B7%9E-%E4%BD%93%E8%82%B2%E4%B8%AD%E5%BF%83/homes?refinement_paths%5B%5D=%2Fhomes&current_tab_id=home_tab&selected_tab_id=home_tab&pets=0&screen_size=medium&hide_dates_and_guests_filters=false&checkin=2022-03-01&checkout=2022-03-03&adults=1&place_id=ChIJo0WAL_z-AjQRBI5IjgL-ckk&map_toggle=false']
    # start_urls = ['https://www.airbnb.cn/']

    def __init__(self, **kwargs):
        self.pageNum = 10
        self.browser = config.getDriver()
        # 写入 cookie
        with open('AirbnbScrapySpider/spiders/cookies.json', 'r', encoding='utf8') as f:
            self.cookies_list = json.loads(f.read())
        super().__init__()

    # def start_requests(self):
    #     response = scrapy.Request(self.start_urls[0], cookies=self.cookies_list, callback=self.parse)
    #     yield response

    def parse(self, response, **kwargs):
        print(response)
        '''
        for i in range(1, 21):
            try:
                item = AirbnbHomeListItem()
                item['name'] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/div[2]/div/div/text()".format(i))[0].extract()
                img = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[1]/div[3]/div/div/div/a/div/img/@src".format(i)).extract_first()
                if not img:
                    img = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/a/div/img/@src".format(i)).extract_first()
                item['img'] = img
                item['price'] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/span/span/span/span/span[2]/text()".format(i))[0].extract()
                shape_and_count = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/div[1]/div/span/span/text()".format(i)).extract()
                item['shape'] = list(shape_and_count)[0]
                item['count'] = list(shape_and_count)[1]
                item['url'] = 'https://www.airbnb.cn' + response.xpath('/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/@href'.format(i)).extract_first()
                item['ID'] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/@href".format(i)).extract_first().split("?")[0].replace("/rooms/", "")
                # 获取更加详细的房屋信息，如评论等
                # yield scrapy.Request(url=item['url'], callback=self.parse_detail)
                yield item  # 将房屋列表存入数据库
            except Exception as e:
                print("=================================")
                print(e.args)
                print("=================================")
        self.pageNum += 1
        # 每个地点只爬 50 页，共 1000 个数据
        if self.pageNum <= 30:
            next_url = self.start_urls[0] + "&items_offset=" + str(20 * self.pageNum)
            # print("======================================================next_url=======================================================================")
            # print(next_url)
            # print("======================================================================================================================================")
            # if next_url:
            response = scrapy.Request(next_url, callback=self.parse, dont_filter=True)
            yield response
        '''

    # 对每一个房屋进行详细访问并解析
    def parse_detail(self, response):
        pass
        # yield scrapy.Request(url=landlord_detail_url, callback=self.parse_landlord_detail, meta={"item": item})  # 通过 参数meta 可以将item参数传递进 callback回调函数,再由 response.meta[...]取出来

    # 对每个房东的信息进行访问解析
    def parse_landlord_detail(self, response):
        pass
        # item = response.meta["item"]  # 获取从response回调函数由meta传过来的 item 值
        # yield item

    def close(self, response):
        self.browser.quit()
