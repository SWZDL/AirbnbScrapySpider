import scrapy
from scrapy import Request
from selenium.webdriver.chrome.options import Options
import pymysql as pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_opt = Options()  # 创建参数设置对象.
# chrome_opt.add_argument('--headless')   # 无界面化.
# chrome_opt.add_argument('--disable-gpu')    # 配合上面的无界面化.
chrome_opt.add_argument('--window-size=1900,1000')  # 设置窗口大小, 窗口大小会有影响.
chrome_opt.add_argument('–disable-infobars')
chrome_opt.add_argument('–incognito')
chrome_opt.add_argument('lang=zh_CN.UTF-8')


class LoginspiderSpider(scrapy.Spider):
    name = 'loginSpider'
    allowed_domains = ['https://www.airbnb.cn/login/']
    start_urls = ['https://www.airbnb.cn/login/']

    def __init__(self, **kwargs):
        self.browser = webdriver.Chrome(executable_path='AirbnbScrapySpider/spiders/chromedriver.exe',
                                        options=chrome_opt)
        super().__init__()

    def parse(self, response):
        pass
