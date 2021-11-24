import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from AirbnbScrapySpider.config import Config  # 导入配置文件

'''导入配置'''
config = Config()
'''配置 selenium'''
chrome_opt = Options()  # 创建参数设置对象.
for option in config.chrome_options:
    chrome_opt.add_argument(option)


class LoginSpider(scrapy.Spider):
    name = 'loginSpider'
    allowed_domains = ['airbnb.cn']
    start_urls = ['https://www.airbnb.cn/login/']

    def __init__(self, **kwargs):
        self.browser = webdriver.Chrome(executable_path='AirbnbScrapySpider/spiders/chromedriver.exe',
                                        options=chrome_opt)
        self.logger.info("login spider start...")
        super().__init__()

    def parse(self, response):
        pass
