import time

import scrapy
from scrapy import Request
from selenium.webdriver.chrome.options import Options
import pymysql as pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlencode

from AirbnbScrapySpider.items import AirbnbHomeListItem

chrome_opt = Options()  # 创建参数设置对象.
# chrome_opt.add_argument('--headless')   # 无界面化.
# chrome_opt.add_argument('--disable-gpu')    # 配合上面的无界面化.
chrome_opt.add_argument('--window-size=1900,1000')  # 设置窗口大小, 窗口大小会有影响.
chrome_opt.add_argument('–disable-infobars')
chrome_opt.add_argument('–incognito')
chrome_opt.add_argument('lang=zh_CN.UTF-8')
custom_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44"}


class HomesListSpider(scrapy.Spider):
    name = 'homesListSpiderGZ'
    allowed_domains = ['airbnb.cn']
    start_urls = ['https://www.airbnb.cn/']

    def __init__(self, **kwargs):
        self.browser = webdriver.Chrome(executable_path='AirbnbScrapySpider/spiders/chromedriver.exe',
                                        options=chrome_opt)
        super().__init__()

    def start_requests(self):
        response = scrapy.Request(self.start_urls[0], callback=self.custom_parse)
        yield response

    def custom_parse(self, response, **kwargs):
        with open("AirbnbScrapySpider/spiders/homes.html", 'wb+') as f:
            f.write(response.body)
        home_lists = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div")
        for home in home_lists:
            item = AirbnbHomeListItem()
            item["name"] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div/div[2]/a/div[2]/div/div").extract()
            item["img"] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div[1]/div[2]/div/div/div/a/div/img")
            item["price"] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div[1]/div/span/span/span/span[1]/span[2]").extract()
            item["score"] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div[2]/div[1]/div/span[2]").extract()
            item["count"] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[2]/span").extract()
            item["shape"] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div[2]/a/div[1]/div/span/span/text()[1]").extract()
            item["number"] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div[2]/a/div[1]/div/span/span/text()[2]").extract()
            # item["url"] = "https://www.airbnb.cn" + home.xpath("/div/div/div/div/div/div/div[2]/a/@href").extract_first()
            # item["ID"] = home.xpath("/div/div/div/div/div/div/div[2]/a/@href").extract_first().split("?")[1].replace("/rooms/", "")
            print("==========================================ITEM===================================================================================")
            print(item)
            print("=============================================================================================================================")
            yield item

        next_url = "https://www.airbnb.cn/" + response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/div/div[1]/nav/div/a[6]/@href").extract_first()
        print("======================================next_url=======================================================================================")
        print(next_url)
        print("=============================================================================================================================")
        if next_url:
            response = scrapy.Request(next_url, callback=self.custom_parse, dont_filter=True)
        yield response

        # 对每一个板块进行详细访问并解析, 获取板块内的每条新闻的url
        # def parse_detail(self, response):
        #     div_res = response.xpath("//div[@class='data_row news_article clearfix ']")
        #     # print(len(div_res))
        #     title = div_res.xpath(".//div[@class='news_title']/h3/a/text()").extract_first()
        #     pic_url = div_res.xpath("./a/img/@src").extract_first()
        #     detail_url = div_res.xpath("//div[@class='news_title']/h3/a/@href").extract_first()
        #     infos = div_res.xpath(".//div[@class='news_tag//text()']").extract()
        #     info_list = []
        #     for info in infos:
        #         info = info.strip()
        #         info_list.append(info)
        #     info_str = "".join(info_list)
        #     item = WangyiproItem()
        #
        #     item["title"] = title
        #     item["detail_url"] = detail_url
        #     item["pic_url"] = pic_url
        #     item["info_str"] = info_str
        #
        #     yield scrapy.Request(url=detail_url, callback=self.parse_content,
        #                          meta={"item": item})  # 通过 参数meta 可以将item参数传递进 callback回调函数,再由 response.meta[...]取出来

        # 对每条新闻的url进行访问, 并解析
        # def parse_content(self, response):
        #     item = response.meta["item"]  # 获取从response回调函数由meta传过来的 item 值
        #     content_list = response.xpath("//div[@class='post_text']/p/text()").extract()
        #     content = "".join(content_list)
        #     item["content"] = content
        #     yield item

    def close(self, response):
        self.browser.quit()
