# 用于模拟登录 Airbnb 并保存 cookie 信息

import scrapy

from AirbnbScrapySpider.config import Config  # 导入配置文件

'''导入配置'''
config = Config()


class LoginSpider(scrapy.Spider):
    name = 'loginSpider'
    allowed_domains = ['airbnb.cn']
    start_urls = ['https://www.airbnb.cn/login']

    def __init__(self, **kwargs):
        self.browser = config.getDriver()
        super().__init__()

    def start_requests(self):
        response = scrapy.Request(self.start_urls[0], callback=self.parse, meta={"flag": "login"})
        yield response

    def parse(self, response, **kwargs):
        print(response)
        self.browser.quit()

    def close(self, response):
        self.browser.quit()
